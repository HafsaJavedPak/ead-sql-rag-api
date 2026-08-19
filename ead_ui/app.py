from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr
import pandas as pd

from ead_ui.client import ApiClientError, EadApiClient, UiSession

API_BASE_URL = os.getenv("EAD_API_BASE_URL", "http://127.0.0.1:8000")
CLIENT = EadApiClient(API_BASE_URL)


def _profile(user: dict[str, Any]) -> str:
    if not user:
        return "Not signed in"
    name = user.get("display_name") or user.get("email")
    return f"**{name}**  \n{user.get('email', '')}  \nRole: `{user.get('role', 'user')}`"


def _choices(items: list[dict[str, Any]]) -> list[tuple[str, str]]:
    return [
        (f"{item['title']} ({item.get('message_count', 0)} messages)", str(item["id"]))
        for item in items
    ]


def _as_frame(run: dict[str, Any] | None) -> pd.DataFrame:
    if not run:
        return pd.DataFrame()
    return pd.DataFrame(run.get("rows") or [], columns=run.get("columns") or None)


def _latest_run(messages: list[dict[str, Any]]) -> dict[str, Any] | None:
    for message in reversed(messages):
        if message.get("run"):
            return message["run"]
    return None


def _chat_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"role": str(item["role"]), "content": str(item.get("content") or "")}
        for item in messages
        if item.get("role") in {"user", "assistant"}
    ]


def _chart_path(run: dict[str, Any] | None, session: UiSession) -> str | None:
    if not run:
        return None
    artifact = next(
        (item for item in run.get("artifacts", []) if item.get("mime_type") == "image/png"),
        None,
    )
    if not artifact:
        return None
    content, _ = CLIENT.artifact(str(artifact["url"]), session)
    handle, name = tempfile.mkstemp(prefix="ead-chart-", suffix=".png")
    os.close(handle)
    Path(name).write_bytes(content)
    return name


def _authenticate(
    action: str,
    email: str,
    password: str,
    display_name: str,
    session: UiSession | None,
) -> tuple[UiSession, str, str, Any, str]:
    current = session or UiSession()
    try:
        if action == "register":
            user = CLIENT.register(email, password, display_name, current)
            status = "Account created and authenticated."
        else:
            user = CLIENT.login(email, password, current)
            status = "Signed in."
        conversations = CLIENT.list_conversations(current)
        return current, _profile(user), status, gr.update(choices=_choices(conversations)), ""
    except (ApiClientError, OSError) as exc:
        return current, _profile(current.user), f"Request failed: {exc}", gr.update(), ""


def register(
    email: str, password: str, display_name: str, session: UiSession | None
) -> tuple[UiSession, str, str, Any, str]:
    return _authenticate("register", email, password, display_name, session)


def login(
    email: str, password: str, session: UiSession | None
) -> tuple[UiSession, str, str, Any, str]:
    return _authenticate("login", email, password, "", session)


def logout(session: UiSession | None) -> tuple[UiSession, str, str, Any, list[Any], Any, str]:
    current = session or UiSession()
    try:
        CLIENT.logout(current)
        status = "Signed out."
    except (ApiClientError, OSError) as exc:
        current.clear()
        status = f"Local session cleared; API logout failed: {exc}"
    return current, _profile({}), status, gr.update(choices=[], value=None), [], None, ""


def refresh_conversations(session: UiSession | None) -> tuple[Any, str]:
    try:
        items = CLIENT.list_conversations(session or UiSession())
        return gr.update(choices=_choices(items)), f"Loaded {len(items)} conversations."
    except (ApiClientError, OSError) as exc:
        return gr.update(), f"Request failed: {exc}"


def create_conversation(
    title: str, session: UiSession | None
) -> tuple[UiSession, Any, list[Any], str, Any, str, str]:
    current = session or UiSession()
    try:
        conversation = CLIENT.create_conversation(title, current)
        items = CLIENT.list_conversations(current)
        return (
            current,
            gr.update(choices=_choices(items), value=str(conversation["id"])),
            [],
            "Conversation created.",
            None,
            "",
            "",
        )
    except (ApiClientError, OSError) as exc:
        return current, gr.update(), [], f"Request failed: {exc}", None, "", ""


def load_conversation(
    conversation_id: str | None, session: UiSession | None
) -> tuple[UiSession, list[dict[str, str]], pd.DataFrame, str | None, str, str]:
    current = session or UiSession()
    if not conversation_id:
        return current, [], pd.DataFrame(), None, "", "Select a conversation."
    try:
        current.conversation_id = conversation_id
        messages = CLIENT.messages(conversation_id, current)
        run = _latest_run(messages)
        return (
            current,
            _chat_messages(messages),
            _as_frame(run),
            _chart_path(run, current),
            str((run or {}).get("validated_sql") or ""),
            f"Loaded {len(messages)} messages.",
        )
    except (ApiClientError, OSError) as exc:
        return current, [], pd.DataFrame(), None, "", f"Request failed: {exc}"


def _terminal_outputs(
    chat: list[dict[str, str]], message: dict[str, Any], session: UiSession
) -> tuple[list[dict[str, str]], str, pd.DataFrame, str | None, str, str]:
    content = str(message.get("content") or "")
    if chat and chat[-1].get("role") == "assistant":
        chat[-1]["content"] = content
    else:
        chat.append({"role": "assistant", "content": content})
    run = message.get("run")
    return (
        chat,
        "Completed.",
        _as_frame(run),
        _chart_path(run, session),
        str((run or {}).get("validated_sql") or ""),
        "",
    )


def send_message(
    content: str,
    mode: str,
    conversation_id: str | None,
    chat: list[dict[str, str]] | None,
    session: UiSession | None,
) -> Iterator[tuple[list[dict[str, str]], str, pd.DataFrame, str | None, str, str]]:
    current = session or UiSession()
    history = list(chat or [])
    question = content.strip()
    if not conversation_id:
        yield history, "Select or create a conversation first.", pd.DataFrame(), None, "", content
        return
    if not question:
        yield history, "Enter a question.", pd.DataFrame(), None, "", content
        return

    history.extend(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "content": ""},
        ]
    )
    yield history, "Submitting...", pd.DataFrame(), None, "", ""
    try:
        if mode == "JSON":
            response = CLIENT.chat(conversation_id, question, current)
            yield _terminal_outputs(history, response["assistant_message"], current)
            return

        answer = ""
        for event in CLIENT.stream_chat(conversation_id, question, current):
            name = event["event"]
            data = event["data"]
            if name == "assistant.delta":
                answer += str(data.get("text") or "")
                history[-1]["content"] = answer
                yield history, "Generating answer...", pd.DataFrame(), None, "", ""
            elif name == "agent.stage":
                yield (
                    history,
                    f"Agent stage: {data.get('stage', 'working')}",
                    pd.DataFrame(),
                    None,
                    "",
                    "",
                )
            elif name == "message.completed":
                yield _terminal_outputs(history, data, current)
                return
            elif name == "run.failed":
                raise ApiClientError(str(data.get("detail") or "Agent run failed."))
            elif name == "run.cancelled":
                yield history, "Run cancelled.", pd.DataFrame(), None, "", ""
                return
    except (ApiClientError, OSError) as exc:
        history[-1]["content"] = f"Request failed: {exc}"
        yield history, f"Request failed: {exc}", pd.DataFrame(), None, "", ""


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="EAD SQL RAG API Console") as demo:
        session = gr.State(UiSession())
        gr.Markdown("# EAD SQL RAG API Console\nAuthenticated end-to-end test client")

        with gr.Row():
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.Tab("Register"):
                        register_email = gr.Textbox(label="Email")
                        register_name = gr.Textbox(label="Display name")
                        register_password = gr.Textbox(label="Password", type="password")
                        register_button = gr.Button("Create account", variant="primary")
                    with gr.Tab("Sign in"):
                        login_email = gr.Textbox(label="Email")
                        login_password = gr.Textbox(label="Password", type="password")
                        login_button = gr.Button("Sign in", variant="primary")
            with gr.Column(scale=1):
                profile = gr.Markdown("Not signed in")
                logout_button = gr.Button("Sign out")
                auth_status = gr.Textbox(label="Session status", interactive=False)

        with gr.Row():
            conversation = gr.Dropdown(label="Conversation", choices=[], scale=3)
            refresh_button = gr.Button("Refresh", scale=1)
        with gr.Row():
            conversation_title = gr.Textbox(label="New conversation title", scale=3)
            create_button = gr.Button("Create", variant="primary", scale=1)

        chatbot = gr.Chatbot(label="Chat", height=440)
        with gr.Row():
            question = gr.Textbox(
                label="Question",
                placeholder="Ask a question about the EAD dataset",
                lines=2,
                scale=4,
            )
            mode = gr.Radio(["Streaming", "JSON"], value="Streaming", label="Response mode")
            send_button = gr.Button("Send", variant="primary", scale=1)
        run_status = gr.Textbox(label="Run status", interactive=False)

        with gr.Tabs():
            with gr.Tab("Result rows"):
                result_rows = gr.Dataframe(label="Result preview", interactive=False)
            with gr.Tab("SQL"):
                sql = gr.Code(label="Validated SQL", language="sql")
            with gr.Tab("Chart"):
                chart = gr.Image(label="Generated chart", type="filepath")

        register_button.click(
            register,
            [register_email, register_password, register_name, session],
            [session, profile, auth_status, conversation, register_password],
        )
        login_button.click(
            login,
            [login_email, login_password, session],
            [session, profile, auth_status, conversation, login_password],
        )
        logout_button.click(
            logout,
            [session],
            [session, profile, auth_status, conversation, chatbot, chart, sql],
        )
        refresh_button.click(
            refresh_conversations,
            [session],
            [conversation, auth_status],
        )
        create_button.click(
            create_conversation,
            [conversation_title, session],
            [session, conversation, chatbot, auth_status, chart, sql, conversation_title],
        )
        conversation.change(
            load_conversation,
            [conversation, session],
            [session, chatbot, result_rows, chart, sql, run_status],
        )
        send_event = send_button.click(
            send_message,
            [question, mode, conversation, chatbot, session],
            [chatbot, run_status, result_rows, chart, sql, question],
        )
        question.submit(
            send_message,
            [question, mode, conversation, chatbot, session],
            [chatbot, run_status, result_rows, chart, sql, question],
        )
        send_event.then(refresh_conversations, [session], [conversation, auth_status])
    return demo


demo = build_ui()


def main() -> None:
    demo.queue(
        default_concurrency_limit=int(os.getenv("GRADIO_DEFAULT_CONCURRENCY_LIMIT", "2")),
        max_size=int(os.getenv("GRADIO_MAX_QUEUE_SIZE", "32")),
    ).launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
        share=False,
        show_error=False,
    )


if __name__ == "__main__":
    main()
