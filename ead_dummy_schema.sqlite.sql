-- Generated from ead_dummy_data_atomcamp.sql.
-- SQLite schema for local SQL-RAG testing; production remains MySQL.
PRAGMA foreign_keys = OFF;

CREATE TABLE "wq_approvalforums" (
  "approvalforum_id" INTEGER PRIMARY KEY,
  "approvalforum_code" TEXT,
  "approvalforum_name" TEXT,
  "approvalforum_slug" TEXT,
  "approvalforum_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_challengs" (
  "challeng_id" INTEGER PRIMARY KEY,
  "challeng_code" TEXT,
  "challeng_name" TEXT,
  "challeng_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_courses" (
  "course_id" INTEGER PRIMARY KEY,
  "course_uuid" TEXT,
  "course_code" TEXT,
  "wing_id" INTEGER,
  "projectsector_id" INTEGER,
  "course_name" TEXT,
  "course_for" INTEGER,
  "course_funding" INTEGER,
  "course_value" REAL,
  "course_label" TEXT,
  "course_mode" INTEGER,
  "course_venue" TEXT,
  "course_startdate" TEXT,
  "course_enddate" TEXT,
  "course_type" TEXT,
  "ftc_meeting_held" TEXT,
  "course_slots" REAL,
  "course_nominee" REAL,
  "approve_nominee" REAL,
  "course_detail" TEXT,
  "course_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_courses_wing_id" ON "wq_courses" ("wing_id");
CREATE INDEX "ix_wq_courses_projectsector_id" ON "wq_courses" ("projectsector_id");

CREATE TABLE "wq_currencies" (
  "currency_id" INTEGER PRIMARY KEY,
  "currency_code" TEXT,
  "currency_name" TEXT,
  "currency_symbol" TEXT,
  "currency_slug" TEXT,
  "currency_base" INTEGER,
  "currency_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_debtexternaldebts" (
  "externaldebt_id" INTEGER PRIMARY KEY,
  "externaldebt_uuid" TEXT,
  "externaldebt_code" TEXT,
  "particulars" TEXT,
  "month" TEXT,
  "fiscal_year" TEXT,
  "month_amount" REAL,
  "fiscalyear_amount" REAL,
  "difference" REAL,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_debtinflows" (
  "infow_id" INTEGER PRIMARY KEY,
  "inflow_uuid" TEXT,
  "inflow_code" TEXT,
  "public_guarntee" INTEGER,
  "financing_source" INTEGER,
  "budget_estimate" REAL,
  "month" TEXT,
  "month_amount" REAL,
  "fiscal_year" TEXT,
  "fiscalyear_amount" REAL,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_debtoutflows" (
  "outflow_id" INTEGER PRIMARY KEY,
  "outflow_uuid" TEXT,
  "outflow_code" TEXT,
  "public_guarntee" INTEGER,
  "financing_source" INTEGER,
  "budget_estimate" REAL,
  "month" TEXT,
  "month_principal" REAL,
  "month_interest" REAL,
  "month_total" REAL,
  "fiscal_year" TEXT,
  "fiscalyear_principal" REAL,
  "fiscalyear_interest" REAL,
  "fiscalyear_total" REAL,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_debtpurposewises" (
  "purpose_id" INTEGER PRIMARY KEY,
  "purpose_uuid" TEXT,
  "purpose_code" TEXT,
  "public_guarntee" INTEGER,
  "kind_aid" INTEGER,
  "purpose" INTEGER,
  "month" TEXT,
  "month_grant" REAL,
  "month_loan" REAL,
  "month_total" REAL,
  "fiscalyear" TEXT,
  "fiscalyear_grant" REAL,
  "fiscalyear_loan" REAL,
  "fiscalyear_total" REAL,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_designations" (
  "designation_id" INTEGER PRIMARY KEY,
  "designation_code" TEXT,
  "designation_name" TEXT,
  "designation_slug" TEXT,
  "designation_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_donors" (
  "donor_id" INTEGER PRIMARY KEY,
  "donor_code" TEXT,
  "donor_name" TEXT,
  "donor_slug" TEXT,
  "donor_color" TEXT,
  "donor_logo" TEXT,
  "donor_type" INTEGER,
  "donor_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_executingagencies" (
  "executingagency_id" INTEGER PRIMARY KEY,
  "executingagency_code" TEXT,
  "executingagency_name" TEXT,
  "executingagency_slug" TEXT,
  "executingagency_status" INTEGER,
  "type" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_faqs" (
  "faq_id" INTEGER PRIMARY KEY,
  "module_id" INTEGER,
  "modulelink_id" INTEGER,
  "faq_code" TEXT,
  "faq_name" TEXT,
  "faq_details" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_faqs_module_id" ON "wq_faqs" ("module_id");
CREATE INDEX "ix_wq_faqs_modulelink_id" ON "wq_faqs" ("modulelink_id");

CREATE TABLE "wq_financialterms" (
  "financialterm_id" INTEGER PRIMARY KEY,
  "wing_id" INTEGER,
  "modalitytype_id" INTEGER,
  "financialterm_code" TEXT,
  "financialterm_name" TEXT,
  "financialterm_status" INTEGER,
  "financialterm_value" TEXT,
  "financial_priority" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_financialterms_wing_id" ON "wq_financialterms" ("wing_id");
CREATE INDEX "ix_wq_financialterms_modalitytype_id" ON "wq_financialterms" ("modalitytype_id");

CREATE TABLE "wq_governmentpartners" (
  "governmentpartner_id" INTEGER PRIMARY KEY,
  "governmentpartner_code" TEXT,
  "governmentpartner_name" TEXT,
  "governmentpartner_slug" TEXT,
  "governmentpartner_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_grantsources" (
  "grantsource_id" INTEGER PRIMARY KEY,
  "wing_id" INTEGER,
  "grantsource_code" TEXT,
  "grantsource_name" TEXT,
  "grantsource_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_grantsources_wing_id" ON "wq_grantsources" ("wing_id");

CREATE TABLE "wq_implementingunits" (
  "implementingunit_id" INTEGER PRIMARY KEY,
  "implementingunit_code" TEXT,
  "implementingunit_name" TEXT,
  "implementingunit_slug" TEXT,
  "implementingunit_logo" TEXT,
  "implementingunit_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_jmccommissions" (
  "jmccommission_id" INTEGER PRIMARY KEY,
  "jmccommission_name" TEXT,
  "jmccommission_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_jmccountries" (
  "country_id" INTEGER PRIMARY KEY,
  "country_code" TEXT,
  "country_name" TEXT,
  "country_slug" TEXT,
  "country_type" TEXT,
  "country_color" TEXT,
  "country_grade" TEXT,
  "established_on" TEXT,
  "country_details" TEXT,
  "country_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_jmcministries" (
  "ministry_id" INTEGER PRIMARY KEY,
  "ministry_code" TEXT,
  "ministry_name" TEXT,
  "ministry_slug" TEXT,
  "ministry_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_jmcsessions" (
  "session_id" INTEGER PRIMARY KEY,
  "session_code" TEXT,
  "country_id" INTEGER,
  "session_title" TEXT,
  "session_slug" TEXT,
  "session_type" INTEGER,
  "session_venue" TEXT,
  "latitude" TEXT,
  "longitude" TEXT,
  "holding_date" TEXT,
  "proposed_date" TEXT,
  "technical_date" TEXT,
  "co_chair_ourside" TEXT,
  "co_chair_countryside" TEXT,
  "session_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_jmcsessions_country_id" ON "wq_jmcsessions" ("country_id");

CREATE TABLE "wq_modalitytypes" (
  "modalitytype_id" INTEGER PRIMARY KEY,
  "projecttype_id" INTEGER,
  "wing_id" INTEGER,
  "modalitytype_code" TEXT,
  "modalitytype_name" TEXT,
  "modalitytype_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_modalitytypes_projecttype_id" ON "wq_modalitytypes" ("projecttype_id");
CREATE INDEX "ix_wq_modalitytypes_wing_id" ON "wq_modalitytypes" ("wing_id");

CREATE TABLE "wq_module" (
  "module_id" INTEGER PRIMARY KEY,
  "module_code" TEXT,
  "module_title" TEXT,
  "module_slug" TEXT,
  "module_active_icon" TEXT,
  "module_inactive_icon" TEXT,
  "module_cover" TEXT,
  "module_order" INTEGER,
  "module_status" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_otp" (
  "otp_id" INTEGER PRIMARY KEY,
  "user_id" INTEGER,
  "otp_code" TEXT,
  "otp_type" TEXT,
  "otp_platform" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_otp_user_id" ON "wq_otp" ("user_id");

CREATE TABLE "wq_outcomes" (
  "outcome_id" INTEGER PRIMARY KEY,
  "outcome_code" TEXT,
  "outcome_color" TEXT,
  "outcome_name" TEXT,
  "outcome_short" TEXT,
  "outcome_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_projectcategories" (
  "category_id" INTEGER PRIMARY KEY,
  "category_code" TEXT,
  "category_name" TEXT,
  "category_slug" TEXT,
  "category_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_projectmodes" (
  "projectmode_id" INTEGER PRIMARY KEY,
  "projectmode_code" TEXT,
  "projectmode_name" TEXT,
  "projectmode_slug" TEXT,
  "projectmode_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_projectsectors" (
  "projectsector_id" INTEGER PRIMARY KEY,
  "projectsector_code" TEXT,
  "projectsector_name" TEXT,
  "projectsector_short" TEXT,
  "projectsector_slug" TEXT,
  "projectsector_color" TEXT,
  "projectsector_status" INTEGER,
  "type" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_projectstatuses" (
  "projectstatus_id" INTEGER PRIMARY KEY,
  "projectstatus_code" TEXT,
  "projectstatus_name" TEXT,
  "projectstatus_slug" TEXT,
  "projectstatus_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_projecttypes" (
  "projecttype_id" INTEGER PRIMARY KEY,
  "projecttype_code" TEXT,
  "projecttype_name" TEXT,
  "projecttype_slug" TEXT,
  "projecttype_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_project_issues" (
  "projectissue_id" INTEGER PRIMARY KEY,
  "projectissue_code" TEXT,
  "projectissue_name" TEXT,
  "projectissue_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_regions" (
  "region_id" INTEGER PRIMARY KEY,
  "region_code" TEXT,
  "region_name" TEXT,
  "region_slug" TEXT,
  "region_color" TEXT,
  "region_logo" TEXT,
  "region_short" TEXT,
  "region_type" INTEGER,
  "region_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_repositories" (
  "repository_id" INTEGER PRIMARY KEY,
  "user_id" INTEGER,
  "wing_id" INTEGER,
  "refrence_code" TEXT,
  "repository_type" TEXT,
  "repository_title" TEXT,
  "repository_file" TEXT,
  "repository_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_repositories_user_id" ON "wq_repositories" ("user_id");
CREATE INDEX "ix_wq_repositories_wing_id" ON "wq_repositories" ("wing_id");

CREATE TABLE "wq_role" (
  "role_id" INTEGER PRIMARY KEY,
  "role_code" TEXT,
  "role_uuid" TEXT,
  "role_title" TEXT,
  "role_slug" TEXT,
  "role_description" TEXT,
  "role_status" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_sdgs" (
  "sdg_id" INTEGER PRIMARY KEY,
  "sdg_code" TEXT,
  "sdg_name" TEXT,
  "sdg_shortname" TEXT,
  "sdg_color" TEXT,
  "sdg_avatar" TEXT,
  "sdg_order" TEXT,
  "sdg_slug" TEXT,
  "sdg_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_servicecadres" (
  "servicecadre_id" INTEGER PRIMARY KEY,
  "servicecadre_name" TEXT,
  "servicecadre_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_sopapprovals" (
  "sopapproval_id" INTEGER PRIMARY KEY,
  "user_id" INTEGER,
  "wing_id" INTEGER,
  "sopapproval_uuid" TEXT,
  "sopapproval_name" TEXT,
  "sopapproval_code" TEXT,
  "sopapproval_remarks" TEXT,
  "sopapproval_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_sopapprovals_user_id" ON "wq_sopapprovals" ("user_id");
CREATE INDEX "ix_wq_sopapprovals_wing_id" ON "wq_sopapprovals" ("wing_id");

CREATE TABLE "wq_sponseragencies" (
  "sponseragency_id" INTEGER PRIMARY KEY,
  "sponseragency_code" TEXT,
  "sponseragency_name" TEXT,
  "sponseragency_slug" TEXT,
  "sponseragency_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_tasks" (
  "task_id" INTEGER PRIMARY KEY,
  "task_uuid" TEXT,
  "task_code" TEXT,
  "task_name" TEXT,
  "task_description" TEXT,
  "task_deadline" TEXT,
  "task_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_timeperiods" (
  "timeperiod_id" INTEGER PRIMARY KEY,
  "timeperiod_code" TEXT,
  "timeperiod_name" TEXT,
  "timeperiod_slug" TEXT,
  "timeperiod_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_users" (
  "user_id" INTEGER PRIMARY KEY,
  "user_uuid" TEXT,
  "user_code" TEXT,
  "user_fullname" TEXT,
  "user_name" TEXT,
  "password" TEXT,
  "_verified" INTEGER,
  "_banned" INTEGER,
  "user_type" INTEGER,
  "action_type" INTEGER,
  "user_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_projects" (
  "project_id" INTEGER PRIMARY KEY,
  "project_uuid" TEXT,
  "project_code" TEXT,
  "project_codeid" TEXT,
  "project_name" TEXT,
  "project_slug" TEXT,
  "project_start" TEXT,
  "project_closing" TEXT,
  "project_effectiveness" TEXT,
  "project_accountopen" INTEGER,
  "project_extended_closing" TEXT,
  "project_wayforward" TEXT,
  "project_scope" TEXT,
  "project_description" TEXT,
  "action_so" INTEGER,
  "action_ds" INTEGER,
  "action_js" INTEGER,
  "project_nature" INTEGER,
  "project_satisfactory" INTEGER,
  "project_status" INTEGER,
  "created_by" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "wq_piplineprojects" (
  "piplineproject_id" INTEGER PRIMARY KEY,
  "piplineproject_uuid" TEXT,
  "piplineproject_code" TEXT,
  "projecttype_id" INTEGER,
  "projectsector_id" INTEGER,
  "currency_id" INTEGER,
  "piplineproject_name" TEXT,
  "piplineproject_slug" TEXT,
  "piplineproject_cost" REAL,
  "exchange_rate" INTEGER,
  "piplineproject_costpkr" INTEGER,
  "piplineproject_costusd" INTEGER,
  "piplineproject_description" TEXT,
  "loan_type" TEXT,
  "cy_wise" REAL,
  "cy_wise_usd" REAL,
  "fy_wise" REAL,
  "fy_wise_usd" REAL,
  "fy_approval_quarter" REAL,
  "fy_approval_quarter_usd" REAL,
  "piplineproject_status" INTEGER,
  "loan_amount" REAL,
  "loan_amount_usd" REAL,
  "loan_amount_type" TEXT,
  "grant_amount" REAL,
  "grant_amount_usd" REAL,
  "grant_amount_type" TEXT,
  "gurantee" TEXT,
  "gurantee_type" TEXT,
  "gurantee_usd" TEXT,
  "pipline_year" TEXT,
  "approval_year" TEXT,
  "approval_quarter" TEXT,
  "ocr_amount_type" TEXT,
  "ocr_amount" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_piplineprojects_projecttype_id" ON "wq_piplineprojects" ("projecttype_id");
CREATE INDEX "ix_wq_piplineprojects_projectsector_id" ON "wq_piplineprojects" ("projectsector_id");
CREATE INDEX "ix_wq_piplineprojects_currency_id" ON "wq_piplineprojects" ("currency_id");

CREATE TABLE "wq_programs" (
  "program_id" INTEGER PRIMARY KEY,
  "program_uuid" TEXT,
  "program_code" TEXT,
  "program_name" TEXT,
  "program_slug" TEXT,
  "currency_id" INTEGER,
  "implementing_agency" TEXT,
  "program_cost" REAL,
  "exchange_rate" REAL,
  "program_costpkr" REAL,
  "program_costusd" REAL,
  "program_disbursement" REAL,
  "program_financingterms" TEXT,
  "program_sign" TEXT,
  "program_closing" TEXT,
  "program_description" TEXT,
  "program_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_wq_programs_currency_id" ON "wq_programs" ("currency_id");

CREATE TABLE "wq_offbudgets" (
  "offbudget_id" INTEGER PRIMARY KEY,
  "offbudget_uuid" TEXT,
  "offbudget_codeid" TEXT,
  "offbudget_code" TEXT,
  "offbudget_name" TEXT,
  "offbudget_implementation" INTEGER,
  "offbudget_slug" TEXT,
  "offbudget_start" TEXT,
  "offbudget_end" TEXT,
  "offbudget_outcomes" TEXT,
  "offbudget_objectives" TEXT,
  "offbudget_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);

CREATE TABLE "cache" (
  "key" INTEGER,
  "value" TEXT,
  "expiration" INTEGER
);

CREATE TABLE "cache_locks" (
  "key" INTEGER,
  "owner" TEXT,
  "expiration" INTEGER
);

CREATE TABLE "course_to_applicants" (
  "to_applicantid" INTEGER,
  "course_id" INTEGER,
  "region_id" INTEGER,
  "applicant_name" TEXT,
  "applicant_dob" TEXT,
  "applicant_passport" TEXT,
  "applicant_responsiblity" TEXT,
  "applicant_grade" TEXT,
  "applicant_education" TEXT,
  "applicant_degree" TEXT,
  "applicant_probation" INTEGER,
  "applicant_blacklist" INTEGER,
  "applicant_joining" TEXT,
  "applicant_scale" TEXT,
  "applicant_department" TEXT,
  "applicant_designation" TEXT,
  "applicant_cnic" TEXT,
  "applicant_cadre" TEXT,
  "applicant_gender" INTEGER,
  "applicant_type" INTEGER,
  "applicant_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_course_to_applicants_course_id" ON "course_to_applicants" ("course_id");
CREATE INDEX "ix_course_to_applicants_region_id" ON "course_to_applicants" ("region_id");

CREATE TABLE "course_to_countries" (
  "to_countryid" INTEGER,
  "course_id" INTEGER,
  "country_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_course_to_countries_course_id" ON "course_to_countries" ("course_id");
CREATE INDEX "ix_course_to_countries_country_id" ON "course_to_countries" ("country_id");

CREATE TABLE "course_to_donors" (
  "to_donorid" INTEGER,
  "course_id" INTEGER,
  "donor_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_course_to_donors_course_id" ON "course_to_donors" ("course_id");
CREATE INDEX "ix_course_to_donors_donor_id" ON "course_to_donors" ("donor_id");

CREATE TABLE "course_to_executingagencies" (
  "to_executingagencyid" INTEGER,
  "course_id" INTEGER,
  "executingagency_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_course_to_executingagencies_course_id" ON "course_to_executingagencies" ("course_id");
CREATE INDEX "ix_course_to_executingagencies_executingagency_id" ON "course_to_executingagencies" ("executingagency_id");

CREATE TABLE "course_to_sectors" (
  "to_sectorid" INTEGER,
  "course_id" INTEGER,
  "sector_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_course_to_sectors_course_id" ON "course_to_sectors" ("course_id");
CREATE INDEX "ix_course_to_sectors_sector_id" ON "course_to_sectors" ("sector_id");

CREATE TABLE "course_to_sponseragencies" (
  "to_sponseragenyid" INTEGER,
  "course_id" INTEGER,
  "sponseragency_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_course_to_sponseragencies_course_id" ON "course_to_sponseragencies" ("course_id");
CREATE INDEX "ix_course_to_sponseragencies_sponseragency_id" ON "course_to_sponseragencies" ("sponseragency_id");

CREATE TABLE "donor_to_types" (
  "todonor_id" INTEGER PRIMARY KEY,
  "donor_id" INTEGER,
  "type" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_donor_to_types_donor_id" ON "donor_to_types" ("donor_id");

CREATE TABLE "failed_jobs" (
  "id" INTEGER PRIMARY KEY,
  "uuid" TEXT,
  "connection" TEXT,
  "queue" TEXT,
  "payload" TEXT,
  "exception" TEXT,
  "failed_at" TEXT
);

CREATE TABLE "faqs_to_attachments" (
  "faqattachment_id" INTEGER PRIMARY KEY,
  "faq_id" INTEGER,
  "attachment_name" TEXT,
  "attachment_file" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_faqs_to_attachments_faq_id" ON "faqs_to_attachments" ("faq_id");

CREATE TABLE "faqs_to_videos" (
  "faqvideo_id" INTEGER PRIMARY KEY,
  "faq_id" INTEGER,
  "video_name" TEXT,
  "video_file" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_faqs_to_videos_faq_id" ON "faqs_to_videos" ("faq_id");

CREATE TABLE "jmccountires_to_areas" (
  "area_id" INTEGER PRIMARY KEY,
  "country_id" INTEGER,
  "area_name" TEXT,
  "area_slug" TEXT,
  "area_code" TEXT,
  "area_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmccountires_to_areas_country_id" ON "jmccountires_to_areas" ("country_id");

CREATE TABLE "jmccountires_to_cochairs" (
  "cochair_id" INTEGER PRIMARY KEY,
  "country_id" INTEGER,
  "cochair_ourside" TEXT,
  "cochair_countryside" TEXT,
  "cochair_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmccountires_to_cochairs_country_id" ON "jmccountires_to_cochairs" ("country_id");

CREATE TABLE "jmccountry_to_traders" (
  "totrade_id" INTEGER PRIMARY KEY,
  "country_id" INTEGER,
  "year" TEXT,
  "export" TEXT,
  "import" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmccountry_to_traders_country_id" ON "jmccountry_to_traders" ("country_id");

CREATE TABLE "jmcsession_to_agendas" (
  "to_agendaid" INTEGER,
  "ministry_id" INTEGER,
  "session_id" INTEGER,
  "agenda_heading" TEXT,
  "agenda_details" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_agendas_ministry_id" ON "jmcsession_to_agendas" ("ministry_id");
CREATE INDEX "ix_jmcsession_to_agendas_session_id" ON "jmcsession_to_agendas" ("session_id");

CREATE TABLE "jmcsession_to_draftprotocols" (
  "to_draftprotocolid" INTEGER,
  "session_id" INTEGER,
  "ministry_id" INTEGER,
  "draftprotocol_title" TEXT,
  "draftprotocol_draftby" TEXT,
  "draftprotocol_date" TEXT,
  "draftprotocol_heading" TEXT,
  "draftprotocol_details" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_draftprotocols_session_id" ON "jmcsession_to_draftprotocols" ("session_id");
CREATE INDEX "ix_jmcsession_to_draftprotocols_ministry_id" ON "jmcsession_to_draftprotocols" ("ministry_id");

CREATE TABLE "jmcsession_to_immfiles" (
  "immfile_id" INTEGER PRIMARY KEY,
  "to_immid" INTEGER,
  "session_id" INTEGER,
  "label" TEXT,
  "attachment" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_immfiles_session_id" ON "jmcsession_to_immfiles" ("session_id");

CREATE TABLE "jmcsession_to_immrenminders" (
  "to_immreminderid" INTEGER,
  "to_immid" INTEGER,
  "session_id" INTEGER,
  "ministry_id" INTEGER,
  "reminder_title" TEXT,
  "reminder_details" TEXT,
  "reminder_deadline" TEXT,
  "reminder_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_immrenminders_session_id" ON "jmcsession_to_immrenminders" ("session_id");
CREATE INDEX "ix_jmcsession_to_immrenminders_ministry_id" ON "jmcsession_to_immrenminders" ("ministry_id");

CREATE TABLE "jmcsession_to_imms" (
  "to_immid" INTEGER,
  "session_id" INTEGER,
  "imm_title" TEXT,
  "imm_type" TEXT,
  "imm_venue" TEXT,
  "imm_date" TEXT,
  "imm_time" TEXT,
  "imm_chair" TEXT,
  "imm_attachments" TEXT,
  "imm_minutes" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_imms_session_id" ON "jmcsession_to_imms" ("session_id");

CREATE TABLE "jmcsession_to_implementations" (
  "toimplementation_id" INTEGER PRIMARY KEY,
  "session_id" INTEGER,
  "ministry_id" INTEGER,
  "to_draftprotocolid" INTEGER,
  "implementation_status" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_implementations_session_id" ON "jmcsession_to_implementations" ("session_id");
CREATE INDEX "ix_jmcsession_to_implementations_ministry_id" ON "jmcsession_to_implementations" ("ministry_id");

CREATE TABLE "jmcsession_to_jmccountries" (
  "to_jmccountryid" INTEGER,
  "session_id" INTEGER,
  "country_id" INTEGER,
  "area_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_jmccountries_session_id" ON "jmcsession_to_jmccountries" ("session_id");
CREATE INDEX "ix_jmcsession_to_jmccountries_country_id" ON "jmcsession_to_jmccountries" ("country_id");
CREATE INDEX "ix_jmcsession_to_jmccountries_area_id" ON "jmcsession_to_jmccountries" ("area_id");

CREATE TABLE "jmcsession_to_proposalfiles" (
  "proposalfile_id" INTEGER PRIMARY KEY,
  "to_proposalid" INTEGER,
  "session_id" INTEGER,
  "label" TEXT,
  "attachment" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_proposalfiles_session_id" ON "jmcsession_to_proposalfiles" ("session_id");

CREATE TABLE "jmcsession_to_proposals" (
  "to_proposalid" INTEGER,
  "session_id" INTEGER,
  "request_id" INTEGER,
  "proposal_title" TEXT,
  "proposal_details" TEXT,
  "proposal_attachment" TEXT,
  "person_name" TEXT,
  "person_email" TEXT,
  "person_contact" TEXT,
  "person_designation" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_proposals_session_id" ON "jmcsession_to_proposals" ("session_id");
CREATE INDEX "ix_jmcsession_to_proposals_request_id" ON "jmcsession_to_proposals" ("request_id");

CREATE TABLE "jmcsession_to_requestfiles" (
  "requestfile_id" INTEGER PRIMARY KEY,
  "request_id" INTEGER,
  "session_id" INTEGER,
  "label" TEXT,
  "attachment" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_requestfiles_request_id" ON "jmcsession_to_requestfiles" ("request_id");
CREATE INDEX "ix_jmcsession_to_requestfiles_session_id" ON "jmcsession_to_requestfiles" ("session_id");

CREATE TABLE "jmcsession_to_requestministries" (
  "requestministry_id" INTEGER PRIMARY KEY,
  "request_id" INTEGER,
  "session_id" INTEGER,
  "ministry_id" INTEGER,
  "status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_requestministries_request_id" ON "jmcsession_to_requestministries" ("request_id");
CREATE INDEX "ix_jmcsession_to_requestministries_session_id" ON "jmcsession_to_requestministries" ("session_id");
CREATE INDEX "ix_jmcsession_to_requestministries_ministry_id" ON "jmcsession_to_requestministries" ("ministry_id");

CREATE TABLE "jmcsession_to_requests" (
  "request_id" INTEGER PRIMARY KEY,
  "session_id" INTEGER,
  "ministry_id" INTEGER,
  "request_title" TEXT,
  "request_details" TEXT,
  "request_deadline" TEXT,
  "request_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_requests_session_id" ON "jmcsession_to_requests" ("session_id");
CREATE INDEX "ix_jmcsession_to_requests_ministry_id" ON "jmcsession_to_requests" ("ministry_id");

CREATE TABLE "jmcsession_to_signedprotocols" (
  "to_signedprotocolid" INTEGER,
  "session_id" INTEGER,
  "protocol_title" TEXT,
  "protocol_date" TEXT,
  "protocol_signedby" TEXT,
  "protocol_details" TEXT,
  "protocol_summary" TEXT,
  "protocol_attachment" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmcsession_to_signedprotocols_session_id" ON "jmcsession_to_signedprotocols" ("session_id");

CREATE TABLE "jmc_logs" (
  "jmclog_id" INTEGER PRIMARY KEY,
  "session_id" INTEGER,
  "user_id" INTEGER,
  "component_name" TEXT,
  "component_data" TEXT,
  "jmclog_json" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmc_logs_session_id" ON "jmc_logs" ("session_id");
CREATE INDEX "ix_jmc_logs_user_id" ON "jmc_logs" ("user_id");

CREATE TABLE "jmc_to_technical_sessions" (
  "technicalsession_id" INTEGER PRIMARY KEY,
  "head_ourside" TEXT,
  "head_countryside" TEXT,
  "session_id" INTEGER,
  "ministries" TEXT,
  "attachment" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_jmc_to_technical_sessions_session_id" ON "jmc_to_technical_sessions" ("session_id");

CREATE TABLE "jobs" (
  "id" INTEGER PRIMARY KEY,
  "queue" TEXT,
  "payload" TEXT,
  "attempts" INTEGER,
  "reserved_at" INTEGER,
  "available_at" INTEGER,
  "created_at" TEXT
);

CREATE TABLE "job_batches" (
  "id" INTEGER PRIMARY KEY,
  "name" TEXT,
  "total_jobs" INTEGER,
  "pending_jobs" INTEGER,
  "failed_jobs" INTEGER,
  "failed_job_ids" TEXT,
  "options" TEXT,
  "cancelled_at" INTEGER,
  "created_at" TEXT,
  "finished_at" INTEGER
);

CREATE TABLE "migrations" (
  "id" INTEGER PRIMARY KEY,
  "migration" TEXT,
  "batch" INTEGER
);

CREATE TABLE "module_to_links" (
  "modulelink_id" INTEGER PRIMARY KEY,
  "module_id" INTEGER,
  "parent_id" INTEGER,
  "modulelink_code" TEXT,
  "link_title" TEXT,
  "link_val" TEXT,
  "link_order" INTEGER,
  "_visibility" INTEGER,
  "icon" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_module_to_links_module_id" ON "module_to_links" ("module_id");
CREATE INDEX "ix_module_to_links_parent_id" ON "module_to_links" ("parent_id");

CREATE TABLE "notifications" (
  "id" INTEGER PRIMARY KEY,
  "type" TEXT,
  "notifiable_type" TEXT,
  "notifiable_id" INTEGER,
  "data" TEXT,
  "read_at" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_notifications_notifiable_id" ON "notifications" ("notifiable_id");

CREATE TABLE "offbudget_to_challengs" (
  "tochalleng_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "challeng_id" INTEGER,
  "issue_text" TEXT,
  "way_forward" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_challengs_offbudget_id" ON "offbudget_to_challengs" ("offbudget_id");
CREATE INDEX "ix_offbudget_to_challengs_challeng_id" ON "offbudget_to_challengs" ("challeng_id");

CREATE TABLE "offbudget_to_disbursments" (
  "todisbursment_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "disbursement_type" TEXT,
  "currency_id" INTEGER,
  "amount" TEXT,
  "exchangerate_usd" TEXT,
  "amount_usd" TEXT,
  "date" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_disbursments_offbudget_id" ON "offbudget_to_disbursments" ("offbudget_id");
CREATE INDEX "ix_offbudget_to_disbursments_currency_id" ON "offbudget_to_disbursments" ("currency_id");

CREATE TABLE "offbudget_to_donors" (
  "todonor_id" INTEGER PRIMARY KEY,
  "donor_id" INTEGER,
  "offbudget_id" INTEGER,
  "currency_id" INTEGER,
  "type" TEXT,
  "amount" TEXT,
  "exchangerate_usd" TEXT,
  "amount_usd" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_donors_donor_id" ON "offbudget_to_donors" ("donor_id");
CREATE INDEX "ix_offbudget_to_donors_offbudget_id" ON "offbudget_to_donors" ("offbudget_id");
CREATE INDEX "ix_offbudget_to_donors_currency_id" ON "offbudget_to_donors" ("currency_id");

CREATE TABLE "offbudget_to_executingagencies" (
  "toexecutingagency_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "executingagency_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_executingagencies_offbudget_id" ON "offbudget_to_executingagencies" ("offbudget_id");
CREATE INDEX "ix_offbudget_to_executingagencies_executingagency_id" ON "offbudget_to_executingagencies" ("executingagency_id");

CREATE TABLE "offbudget_to_financials" (
  "tofinancial_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "currency_id" INTEGER,
  "amount" TEXT,
  "amount_pkr" TEXT,
  "amount_usd" TEXT,
  "exchangerate_usd" INTEGER,
  "exchangerate_pkr" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_financials_offbudget_id" ON "offbudget_to_financials" ("offbudget_id");
CREATE INDEX "ix_offbudget_to_financials_currency_id" ON "offbudget_to_financials" ("currency_id");

CREATE TABLE "offbudget_to_governmentpartners" (
  "togovernmentpartner_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "governmentpartner_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_governmentpartners_offbudget_id" ON "offbudget_to_governmentpartners" ("offbudget_id");
CREATE INDEX "ix_offbudget_to_governmentpartners_governmentpartner_id" ON "offbudget_to_governmentpartners" ("governmentpartner_id");

CREATE TABLE "offbudget_to_outcomes" (
  "offbudgetoutcome_id" INTEGER PRIMARY KEY,
  "outcome_id" INTEGER,
  "offbudget_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_outcomes_outcome_id" ON "offbudget_to_outcomes" ("outcome_id");
CREATE INDEX "ix_offbudget_to_outcomes_offbudget_id" ON "offbudget_to_outcomes" ("offbudget_id");

CREATE TABLE "offbudget_to_regions" (
  "toregion_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "region_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_regions_offbudget_id" ON "offbudget_to_regions" ("offbudget_id");
CREATE INDEX "ix_offbudget_to_regions_region_id" ON "offbudget_to_regions" ("region_id");

CREATE TABLE "offbudget_to_remarks" (
  "toremarks_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "remarks" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_remarks_offbudget_id" ON "offbudget_to_remarks" ("offbudget_id");

CREATE TABLE "offbudget_to_sdgs" (
  "tosdg_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "sdg_id" INTEGER,
  "remarks" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_offbudget_to_sdgs_offbudget_id" ON "offbudget_to_sdgs" ("offbudget_id");
CREATE INDEX "ix_offbudget_to_sdgs_sdg_id" ON "offbudget_to_sdgs" ("sdg_id");

CREATE TABLE "password_reset_tokens" (
  "email" INTEGER,
  "token" TEXT,
  "created_at" TEXT
);

CREATE TABLE "personal_access_tokens" (
  "id" INTEGER PRIMARY KEY,
  "tokenable_type" TEXT,
  "tokenable_id" INTEGER,
  "name" TEXT,
  "token" TEXT,
  "abilities" TEXT,
  "last_used_at" TEXT,
  "expires_at" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_personal_access_tokens_tokenable_id" ON "personal_access_tokens" ("tokenable_id");

CREATE TABLE "piplineprojects_to_approvalforums" (
  "to_approvalforumid" INTEGER,
  "piplineproject_id" INTEGER,
  "approvalforum_id" INTEGER,
  "approvalforum_date" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_piplineprojects_to_approvalforums_piplineproject_id" ON "piplineprojects_to_approvalforums" ("piplineproject_id");
CREATE INDEX "ix_piplineprojects_to_approvalforums_approvalforum_id" ON "piplineprojects_to_approvalforums" ("approvalforum_id");

CREATE TABLE "piplineprojects_to_donors" (
  "todonor_id" INTEGER PRIMARY KEY,
  "piplineproject_id" INTEGER,
  "donor_id" INTEGER,
  "type" TEXT,
  "terms" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_piplineprojects_to_donors_piplineproject_id" ON "piplineprojects_to_donors" ("piplineproject_id");
CREATE INDEX "ix_piplineprojects_to_donors_donor_id" ON "piplineprojects_to_donors" ("donor_id");

CREATE TABLE "piplineprojects_to_regions" (
  "to_regionid" INTEGER,
  "piplineproject_id" INTEGER,
  "region_id" INTEGER,
  "latitude" TEXT,
  "longitude" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_piplineprojects_to_regions_piplineproject_id" ON "piplineprojects_to_regions" ("piplineproject_id");
CREATE INDEX "ix_piplineprojects_to_regions_region_id" ON "piplineprojects_to_regions" ("region_id");

CREATE TABLE "piplineproject_logs" (
  "piplineprojectlog_id" INTEGER PRIMARY KEY,
  "piplineproject_id" INTEGER,
  "user_id" INTEGER,
  "component_name" TEXT,
  "component_data" TEXT,
  "pipelineproject_json" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_piplineproject_logs_piplineproject_id" ON "piplineproject_logs" ("piplineproject_id");
CREATE INDEX "ix_piplineproject_logs_user_id" ON "piplineproject_logs" ("user_id");

CREATE TABLE "piplineproject_to_wings" (
  "piplineprojecttowings_id" INTEGER PRIMARY KEY,
  "piplineproject_id" INTEGER,
  "user_id" INTEGER,
  "wing_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_piplineproject_to_wings_piplineproject_id" ON "piplineproject_to_wings" ("piplineproject_id");
CREATE INDEX "ix_piplineproject_to_wings_user_id" ON "piplineproject_to_wings" ("user_id");
CREATE INDEX "ix_piplineproject_to_wings_wing_id" ON "piplineproject_to_wings" ("wing_id");

CREATE TABLE "pipline_to_donorterms" (
  "toterm_id" INTEGER PRIMARY KEY,
  "piplineproject_id" INTEGER,
  "todonor_id" INTEGER,
  "financialterm_id" INTEGER,
  "financialterm_value" INTEGER,
  "modality_type" INTEGER,
  "repayment_date" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_pipline_to_donorterms_piplineproject_id" ON "pipline_to_donorterms" ("piplineproject_id");
CREATE INDEX "ix_pipline_to_donorterms_todonor_id" ON "pipline_to_donorterms" ("todonor_id");
CREATE INDEX "ix_pipline_to_donorterms_financialterm_id" ON "pipline_to_donorterms" ("financialterm_id");

CREATE TABLE "pipline_to_projecttypes" (
  "to_piplineprojecttype_id" INTEGER PRIMARY KEY,
  "piplineproject_id" INTEGER,
  "projecttype_id" INTEGER,
  "currency_id" INTEGER,
  "amount" TEXT,
  "exchange_rate" TEXT,
  "amount_usd" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_pipline_to_projecttypes_piplineproject_id" ON "pipline_to_projecttypes" ("piplineproject_id");
CREATE INDEX "ix_pipline_to_projecttypes_projecttype_id" ON "pipline_to_projecttypes" ("projecttype_id");
CREATE INDEX "ix_pipline_to_projecttypes_currency_id" ON "pipline_to_projecttypes" ("currency_id");

CREATE TABLE "program_logs" (
  "programlog_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "user_id" INTEGER,
  "component_name" TEXT,
  "component_data" TEXT,
  "programlog_json" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_logs_program_id" ON "program_logs" ("program_id");
CREATE INDEX "ix_program_logs_user_id" ON "program_logs" ("user_id");

CREATE TABLE "program_to_approvalforums" (
  "toapprovalforum_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "approvalforum_id" INTEGER,
  "approvalforum_date" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_to_approvalforums_program_id" ON "program_to_approvalforums" ("program_id");
CREATE INDEX "ix_program_to_approvalforums_approvalforum_id" ON "program_to_approvalforums" ("approvalforum_id");

CREATE TABLE "program_to_donors" (
  "todonor_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "donor_id" INTEGER,
  "type" TEXT,
  "terms" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_to_donors_program_id" ON "program_to_donors" ("program_id");
CREATE INDEX "ix_program_to_donors_donor_id" ON "program_to_donors" ("donor_id");

CREATE TABLE "program_to_donorterms" (
  "toterm_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "todonor_id" INTEGER,
  "financialterm_id" INTEGER,
  "financialterm_value" INTEGER,
  "modality_type" INTEGER,
  "repayment_date" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_to_donorterms_program_id" ON "program_to_donorterms" ("program_id");
CREATE INDEX "ix_program_to_donorterms_todonor_id" ON "program_to_donorterms" ("todonor_id");
CREATE INDEX "ix_program_to_donorterms_financialterm_id" ON "program_to_donorterms" ("financialterm_id");

CREATE TABLE "program_to_executinagencies" (
  "toexecutingagency_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "executingagency_id" INTEGER,
  "terms" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_to_executinagencies_program_id" ON "program_to_executinagencies" ("program_id");
CREATE INDEX "ix_program_to_executinagencies_executingagency_id" ON "program_to_executinagencies" ("executingagency_id");

CREATE TABLE "program_to_regions" (
  "toregion_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "region_id" INTEGER,
  "latitude" TEXT,
  "longitude" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_to_regions_program_id" ON "program_to_regions" ("program_id");
CREATE INDEX "ix_program_to_regions_region_id" ON "program_to_regions" ("region_id");

CREATE TABLE "program_to_sectors" (
  "tosector_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "projectsector_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_to_sectors_program_id" ON "program_to_sectors" ("program_id");
CREATE INDEX "ix_program_to_sectors_projectsector_id" ON "program_to_sectors" ("projectsector_id");

CREATE TABLE "program_to_sponseragencies" (
  "tosponseragency_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "sponseragency_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_to_sponseragencies_program_id" ON "program_to_sponseragencies" ("program_id");
CREATE INDEX "ix_program_to_sponseragencies_sponseragency_id" ON "program_to_sponseragencies" ("sponseragency_id");

CREATE TABLE "program_to_wings" (
  "programtowings_id" INTEGER PRIMARY KEY,
  "program_id" INTEGER,
  "user_id" INTEGER,
  "wing_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_program_to_wings_program_id" ON "program_to_wings" ("program_id");
CREATE INDEX "ix_program_to_wings_user_id" ON "program_to_wings" ("user_id");
CREATE INDEX "ix_program_to_wings_wing_id" ON "program_to_wings" ("wing_id");

CREATE TABLE "projectsector_to_subsectors" (
  "subsector_id" INTEGER PRIMARY KEY,
  "projectsector_id" INTEGER,
  "subsector_code" TEXT,
  "subsector_name" TEXT,
  "subsector_color" TEXT,
  "subsector_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_projectsector_to_subsectors_projectsector_id" ON "projectsector_to_subsectors" ("projectsector_id");

CREATE TABLE "project_logs" (
  "projectlog_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "user_id" INTEGER,
  "component_name" TEXT,
  "component_data" TEXT,
  "projectlog_json" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_logs_project_id" ON "project_logs" ("project_id");
CREATE INDEX "ix_project_logs_user_id" ON "project_logs" ("user_id");

CREATE TABLE "project_to_approvalforums" (
  "projecttoapprovalforum_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "approvalforum_id" INTEGER,
  "approvalforum_date" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_approvalforums_project_id" ON "project_to_approvalforums" ("project_id");
CREATE INDEX "ix_project_to_approvalforums_approvalforum_id" ON "project_to_approvalforums" ("approvalforum_id");

CREATE TABLE "project_to_categories" (
  "projecttocategory_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "category_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_categories_project_id" ON "project_to_categories" ("project_id");
CREATE INDEX "ix_project_to_categories_category_id" ON "project_to_categories" ("category_id");

CREATE TABLE "project_to_disbursementdetails" (
  "projectdisbursementdetail_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "projectdisbursement_id" INTEGER,
  "timeperiod_id" INTEGER,
  "currency_id" INTEGER,
  "sum_type" TEXT,
  "detail_type" TEXT,
  "from" TEXT,
  "to" TEXT,
  "amount" TEXT,
  "amount_usd" TEXT,
  "exchangerate_usd" REAL,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_disbursementdetails_project_id" ON "project_to_disbursementdetails" ("project_id");
CREATE INDEX "ix_project_to_disbursementdetails_projectdisbursement_id" ON "project_to_disbursementdetails" ("projectdisbursement_id");
CREATE INDEX "ix_project_to_disbursementdetails_timeperiod_id" ON "project_to_disbursementdetails" ("timeperiod_id");
CREATE INDEX "ix_project_to_disbursementdetails_currency_id" ON "project_to_disbursementdetails" ("currency_id");

CREATE TABLE "project_to_disbursements" (
  "projectdisbursement_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "disbursement_type" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_disbursements_project_id" ON "project_to_disbursements" ("project_id");

CREATE TABLE "project_to_executingencies" (
  "projecttoexecutingency_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "executingagency_id" INTEGER,
  "region_id" INTEGER,
  "latitude" TEXT,
  "longitude" TEXT,
  "pd_name" TEXT,
  "pd_email" TEXT,
  "pd_contact" TEXT,
  "implementing_unit" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_executingencies_project_id" ON "project_to_executingencies" ("project_id");
CREATE INDEX "ix_project_to_executingencies_executingagency_id" ON "project_to_executingencies" ("executingagency_id");
CREATE INDEX "ix_project_to_executingencies_region_id" ON "project_to_executingencies" ("region_id");

CREATE TABLE "project_to_extentions" (
  "projecttoextention_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "extension_label" TEXT,
  "extension_date" TEXT,
  "extension_remarks" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_extentions_project_id" ON "project_to_extentions" ("project_id");

CREATE TABLE "project_to_financialdistributions" (
  "financialdistribution_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "region_id" INTEGER,
  "currency_id" INTEGER,
  "amount" TEXT,
  "amount_usd" TEXT,
  "exchange_rate" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_financialdistributions_project_id" ON "project_to_financialdistributions" ("project_id");
CREATE INDEX "ix_project_to_financialdistributions_region_id" ON "project_to_financialdistributions" ("region_id");
CREATE INDEX "ix_project_to_financialdistributions_currency_id" ON "project_to_financialdistributions" ("currency_id");

CREATE TABLE "project_to_financials" (
  "projecttofinancial_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "projectcost_currency" INTEGER,
  "project_cost" REAL,
  "projectcost_exchange" REAL,
  "projectcost_usdexchange" REAL,
  "projectcost_pkr" REAL,
  "projectcost_usd" REAL,
  "loan_amount" REAL,
  "loan_amountusd" REAL,
  "loan_currency" INTEGER,
  "loan_id" TEXT,
  "grant_amount" REAL,
  "grant_amountusd" REAL,
  "grant_currency" INTEGER,
  "grand_id" TEXT,
  "local_component" REAL,
  "financial_close" INTEGER,
  "local_componentcurrency" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_financials_project_id" ON "project_to_financials" ("project_id");
CREATE INDEX "ix_project_to_financials_loan_id" ON "project_to_financials" ("loan_id");
CREATE INDEX "ix_project_to_financials_grand_id" ON "project_to_financials" ("grand_id");

CREATE TABLE "project_to_foreigncecomponents" (
  "projecttoforeigncecomponent_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "donor_id" INTEGER,
  "exchangerate_usd" REAL,
  "loan_currency" INTEGER,
  "loan_amount" REAL,
  "loan_amount_usd" REAL,
  "grant_currency" INTEGER,
  "grant_amount" REAL,
  "grant_amount_usd" REAL,
  "graceperiod_from" TEXT,
  "graceperiod_to" TEXT,
  "initial_approval" TEXT,
  "type" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_foreigncecomponents_project_id" ON "project_to_foreigncecomponents" ("project_id");
CREATE INDEX "ix_project_to_foreigncecomponents_donor_id" ON "project_to_foreigncecomponents" ("donor_id");

CREATE TABLE "project_to_foreigncecomponentterms" (
  "toterm_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "projecttoforeigndetail_id" INTEGER,
  "financialterm_id" INTEGER,
  "financialterm_value" TEXT,
  "modality_type" INTEGER,
  "repayment_date" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_foreigncecomponentterms_project_id" ON "project_to_foreigncecomponentterms" ("project_id");
CREATE INDEX "ix_project_to_foreigncecomponentterms_projecttoforeigndetail_id" ON "project_to_foreigncecomponentterms" ("projecttoforeigndetail_id");
CREATE INDEX "ix_project_to_foreigncecomponentterms_financialterm_id" ON "project_to_foreigncecomponentterms" ("financialterm_id");

CREATE TABLE "project_to_foreigndetails" (
  "projecttoforeigndetail_id" INTEGER PRIMARY KEY,
  "projecttoforeigncecomponent_id" INTEGER,
  "project_id" INTEGER,
  "donor_id" INTEGER,
  "type" TEXT,
  "modalitytype_id" INTEGER,
  "grantsource_id" INTEGER,
  "currency_id" INTEGER,
  "id" TEXT,
  "amount" REAL,
  "amount_usd" REAL,
  "exchange_rate" REAL,
  "graceperiod_from" TEXT,
  "graceperiod_to" TEXT,
  "initial_approval" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_foreigndetails_projecttoforeigncecomponent_id" ON "project_to_foreigndetails" ("projecttoforeigncecomponent_id");
CREATE INDEX "ix_project_to_foreigndetails_project_id" ON "project_to_foreigndetails" ("project_id");
CREATE INDEX "ix_project_to_foreigndetails_donor_id" ON "project_to_foreigndetails" ("donor_id");
CREATE INDEX "ix_project_to_foreigndetails_modalitytype_id" ON "project_to_foreigndetails" ("modalitytype_id");
CREATE INDEX "ix_project_to_foreigndetails_grantsource_id" ON "project_to_foreigndetails" ("grantsource_id");
CREATE INDEX "ix_project_to_foreigndetails_currency_id" ON "project_to_foreigndetails" ("currency_id");

CREATE TABLE "project_to_issues" (
  "toissue_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "projectissue_id" INTEGER,
  "remarks" TEXT,
  "wayforward" TEXT,
  "issue_order" INTEGER,
  "projectissue_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_issues_project_id" ON "project_to_issues" ("project_id");
CREATE INDEX "ix_project_to_issues_projectissue_id" ON "project_to_issues" ("projectissue_id");

CREATE TABLE "project_to_localcomponents" (
  "localcomponent_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "region_id" INTEGER,
  "currency_id" INTEGER,
  "amount" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_localcomponents_project_id" ON "project_to_localcomponents" ("project_id");
CREATE INDEX "ix_project_to_localcomponents_region_id" ON "project_to_localcomponents" ("region_id");
CREATE INDEX "ix_project_to_localcomponents_currency_id" ON "project_to_localcomponents" ("currency_id");

CREATE TABLE "project_to_parallels" (
  "projectparallel_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "project_parallel" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_parallels_project_id" ON "project_to_parallels" ("project_id");

CREATE TABLE "project_to_physicalprogresses" (
  "projecttophysicalprogress_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "progress_label" TEXT,
  "progress_remarks" TEXT,
  "from_quarter" TEXT,
  "from_year" TEXT,
  "to_quarter" TEXT,
  "to_year" TEXT,
  "progress_completion" TEXT,
  "action_taken" TEXT,
  "status" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_physicalprogresses_project_id" ON "project_to_physicalprogresses" ("project_id");

CREATE TABLE "project_to_projectmodes" (
  "projecttoprojectmode_id" INTEGER PRIMARY KEY,
  "projectmode_id" INTEGER,
  "project_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_projectmodes_projectmode_id" ON "project_to_projectmodes" ("projectmode_id");
CREATE INDEX "ix_project_to_projectmodes_project_id" ON "project_to_projectmodes" ("project_id");

CREATE TABLE "project_to_projectsectors" (
  "projecttoprojectsector_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "projectsector_id" INTEGER,
  "subsector_id" INTEGER,
  "currency_id" INTEGER,
  "sector_amount" TEXT,
  "sector_usdamount" TEXT,
  "exchange_rate" REAL,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_projectsectors_project_id" ON "project_to_projectsectors" ("project_id");
CREATE INDEX "ix_project_to_projectsectors_projectsector_id" ON "project_to_projectsectors" ("projectsector_id");
CREATE INDEX "ix_project_to_projectsectors_subsector_id" ON "project_to_projectsectors" ("subsector_id");
CREATE INDEX "ix_project_to_projectsectors_currency_id" ON "project_to_projectsectors" ("currency_id");

CREATE TABLE "project_to_projecttypes" (
  "projecttoprojecttype_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "projecttype_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_projecttypes_project_id" ON "project_to_projecttypes" ("project_id");
CREATE INDEX "ix_project_to_projecttypes_projecttype_id" ON "project_to_projecttypes" ("projecttype_id");

CREATE TABLE "project_to_regioncosts" (
  "to_regioncostid" INTEGER,
  "project_id" INTEGER,
  "region_id" INTEGER,
  "currency_id" INTEGER,
  "amount" TEXT,
  "exchange_rate" TEXT,
  "amount_usd" TEXT,
  "type" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_regioncosts_project_id" ON "project_to_regioncosts" ("project_id");
CREATE INDEX "ix_project_to_regioncosts_region_id" ON "project_to_regioncosts" ("region_id");
CREATE INDEX "ix_project_to_regioncosts_currency_id" ON "project_to_regioncosts" ("currency_id");

CREATE TABLE "project_to_revisedcosts" (
  "projecttorevisedcost_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "revised_cost" REAL,
  "revisedcost_currency" INTEGER,
  "revisedcost_exchange" REAL,
  "revisedcost_pkr" REAL,
  "revisedcost_usd" REAL,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_revisedcosts_project_id" ON "project_to_revisedcosts" ("project_id");

CREATE TABLE "project_to_revisondates" (
  "projecttorevisondate_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "revision_date" TEXT,
  "revision_remarks" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_revisondates_project_id" ON "project_to_revisondates" ("project_id");

CREATE TABLE "project_to_scopes" (
  "toscope_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "remarks" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_scopes_project_id" ON "project_to_scopes" ("project_id");

CREATE TABLE "project_to_sponsoragencies" (
  "projecttosponsoragency_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "sponseragency_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_sponsoragencies_project_id" ON "project_to_sponsoragencies" ("project_id");
CREATE INDEX "ix_project_to_sponsoragencies_sponseragency_id" ON "project_to_sponsoragencies" ("sponseragency_id");

CREATE TABLE "project_to_umbrella" (
  "projectumbrella_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "project_umbrella" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_umbrella_project_id" ON "project_to_umbrella" ("project_id");

CREATE TABLE "project_to_wings" (
  "projecttowing_id" INTEGER PRIMARY KEY,
  "project_id" INTEGER,
  "user_id" INTEGER,
  "wing_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_project_to_wings_project_id" ON "project_to_wings" ("project_id");
CREATE INDEX "ix_project_to_wings_user_id" ON "project_to_wings" ("user_id");
CREATE INDEX "ix_project_to_wings_wing_id" ON "project_to_wings" ("wing_id");

CREATE TABLE "remark_to_sdgs" (
  "tosdg_id" INTEGER PRIMARY KEY,
  "offbudget_id" INTEGER,
  "toremarks_id" INTEGER,
  "sdg_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_remark_to_sdgs_offbudget_id" ON "remark_to_sdgs" ("offbudget_id");
CREATE INDEX "ix_remark_to_sdgs_toremarks_id" ON "remark_to_sdgs" ("toremarks_id");
CREATE INDEX "ix_remark_to_sdgs_sdg_id" ON "remark_to_sdgs" ("sdg_id");

CREATE TABLE "role_to_links" (
  "rolelink_id" INTEGER PRIMARY KEY,
  "modulelink_id" INTEGER,
  "role_id" INTEGER,
  "rolelink_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_role_to_links_modulelink_id" ON "role_to_links" ("modulelink_id");
CREATE INDEX "ix_role_to_links_role_id" ON "role_to_links" ("role_id");

CREATE TABLE "role_to_module" (
  "rolemodule_id" INTEGER PRIMARY KEY,
  "role_id" INTEGER,
  "module_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_role_to_module_role_id" ON "role_to_module" ("role_id");
CREATE INDEX "ix_role_to_module_module_id" ON "role_to_module" ("module_id");

CREATE TABLE "sessions" (
  "id" INTEGER PRIMARY KEY,
  "user_id" INTEGER,
  "ip_address" TEXT,
  "user_agent" TEXT,
  "payload" TEXT,
  "last_activity" INTEGER
);
CREATE INDEX "ix_sessions_user_id" ON "sessions" ("user_id");

CREATE TABLE "task_mark_to_user" (
  "taskmark_id" INTEGER PRIMARY KEY,
  "task_id" INTEGER,
  "user_id" INTEGER,
  "task_deadline" TEXT,
  "mark_description" TEXT,
  "mark_type" INTEGER,
  "mark_by" INTEGER,
  "action_taken" INTEGER,
  "task_log" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_task_mark_to_user_task_id" ON "task_mark_to_user" ("task_id");
CREATE INDEX "ix_task_mark_to_user_user_id" ON "task_mark_to_user" ("user_id");

CREATE TABLE "task_to_attachments" (
  "taskattachment_id" INTEGER PRIMARY KEY,
  "task_id" INTEGER,
  "taskmark_id" INTEGER,
  "user_id" INTEGER,
  "attachment_label" TEXT,
  "attachment_file" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_task_to_attachments_task_id" ON "task_to_attachments" ("task_id");
CREATE INDEX "ix_task_to_attachments_taskmark_id" ON "task_to_attachments" ("taskmark_id");
CREATE INDEX "ix_task_to_attachments_user_id" ON "task_to_attachments" ("user_id");

CREATE TABLE "task_to_seen" (
  "task_seenid" INTEGER,
  "task_id" INTEGER,
  "seen_at" TEXT,
  "taskmark_id" INTEGER,
  "user_id" INTEGER,
  "seen_status" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_task_to_seen_task_id" ON "task_to_seen" ("task_id");
CREATE INDEX "ix_task_to_seen_taskmark_id" ON "task_to_seen" ("taskmark_id");
CREATE INDEX "ix_task_to_seen_user_id" ON "task_to_seen" ("user_id");

CREATE TABLE "user_to_ministries" (
  "usertoministry_id" INTEGER PRIMARY KEY,
  "user_id" INTEGER,
  "ministry_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_user_to_ministries_user_id" ON "user_to_ministries" ("user_id");
CREATE INDEX "ix_user_to_ministries_ministry_id" ON "user_to_ministries" ("ministry_id");

CREATE TABLE "user_to_profile" (
  "userprofile_id" INTEGER PRIMARY KEY,
  "user_id" INTEGER,
  "avatar" TEXT,
  "contact" TEXT,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_user_to_profile_user_id" ON "user_to_profile" ("user_id");

CREATE TABLE "user_to_role" (
  "userrole_id" INTEGER PRIMARY KEY,
  "user_id" INTEGER,
  "role_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_user_to_role_user_id" ON "user_to_role" ("user_id");
CREATE INDEX "ix_user_to_role_role_id" ON "user_to_role" ("role_id");

CREATE TABLE "user_to_wings" (
  "usertowing_id" INTEGER PRIMARY KEY,
  "user_id" INTEGER,
  "wing_id" INTEGER,
  "created_at" TEXT,
  "updated_at" TEXT
);
CREATE INDEX "ix_user_to_wings_user_id" ON "user_to_wings" ("user_id");
CREATE INDEX "ix_user_to_wings_wing_id" ON "user_to_wings" ("wing_id");

