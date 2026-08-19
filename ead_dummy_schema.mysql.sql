-- Generated from ead_dummy_data_atomcamp.sql.
-- MySQL schema for the synthetic SQL-RAG test dataset.
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE `wq_approvalforums` (
  `approvalforum_id` BIGINT NOT NULL PRIMARY KEY,
  `approvalforum_code` VARCHAR(255) NULL,
  `approvalforum_name` VARCHAR(255) NULL,
  `approvalforum_slug` VARCHAR(255) NULL,
  `approvalforum_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_challengs` (
  `challeng_id` BIGINT NOT NULL PRIMARY KEY,
  `challeng_code` VARCHAR(255) NULL,
  `challeng_name` VARCHAR(255) NULL,
  `challeng_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_courses` (
  `course_id` BIGINT NOT NULL PRIMARY KEY,
  `course_uuid` VARCHAR(255) NULL,
  `course_code` VARCHAR(255) NULL,
  `wing_id` BIGINT NULL,
  `projectsector_id` BIGINT NULL,
  `course_name` VARCHAR(255) NULL,
  `course_for` BIGINT NULL,
  `course_funding` BIGINT NULL,
  `course_value` DOUBLE NULL,
  `course_label` VARCHAR(255) NULL,
  `course_mode` BIGINT NULL,
  `course_venue` VARCHAR(255) NULL,
  `course_startdate` VARCHAR(255) NULL,
  `course_enddate` VARCHAR(255) NULL,
  `course_type` VARCHAR(255) NULL,
  `ftc_meeting_held` VARCHAR(255) NULL,
  `course_slots` DOUBLE NULL,
  `course_nominee` DOUBLE NULL,
  `approve_nominee` DOUBLE NULL,
  `course_detail` VARCHAR(255) NULL,
  `course_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_courses_wing_id` (`wing_id`),
  KEY `ix_wq_courses_projectsector_id` (`projectsector_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_currencies` (
  `currency_id` BIGINT NOT NULL PRIMARY KEY,
  `currency_code` VARCHAR(255) NULL,
  `currency_name` VARCHAR(255) NULL,
  `currency_symbol` VARCHAR(255) NULL,
  `currency_slug` VARCHAR(255) NULL,
  `currency_base` BIGINT NULL,
  `currency_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_debtexternaldebts` (
  `externaldebt_id` BIGINT NOT NULL PRIMARY KEY,
  `externaldebt_uuid` VARCHAR(255) NULL,
  `externaldebt_code` VARCHAR(255) NULL,
  `particulars` VARCHAR(255) NULL,
  `month` VARCHAR(255) NULL,
  `fiscal_year` VARCHAR(255) NULL,
  `month_amount` DOUBLE NULL,
  `fiscalyear_amount` DOUBLE NULL,
  `difference` DOUBLE NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_debtinflows` (
  `infow_id` BIGINT NOT NULL PRIMARY KEY,
  `inflow_uuid` VARCHAR(255) NULL,
  `inflow_code` VARCHAR(255) NULL,
  `public_guarntee` BIGINT NULL,
  `financing_source` BIGINT NULL,
  `budget_estimate` DOUBLE NULL,
  `month` VARCHAR(255) NULL,
  `month_amount` DOUBLE NULL,
  `fiscal_year` VARCHAR(255) NULL,
  `fiscalyear_amount` DOUBLE NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_debtoutflows` (
  `outflow_id` BIGINT NOT NULL PRIMARY KEY,
  `outflow_uuid` VARCHAR(255) NULL,
  `outflow_code` VARCHAR(255) NULL,
  `public_guarntee` BIGINT NULL,
  `financing_source` BIGINT NULL,
  `budget_estimate` DOUBLE NULL,
  `month` VARCHAR(255) NULL,
  `month_principal` DOUBLE NULL,
  `month_interest` DOUBLE NULL,
  `month_total` DOUBLE NULL,
  `fiscal_year` VARCHAR(255) NULL,
  `fiscalyear_principal` DOUBLE NULL,
  `fiscalyear_interest` DOUBLE NULL,
  `fiscalyear_total` DOUBLE NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_debtpurposewises` (
  `purpose_id` BIGINT NOT NULL PRIMARY KEY,
  `purpose_uuid` VARCHAR(255) NULL,
  `purpose_code` VARCHAR(255) NULL,
  `public_guarntee` BIGINT NULL,
  `kind_aid` BIGINT NULL,
  `purpose` BIGINT NULL,
  `month` VARCHAR(255) NULL,
  `month_grant` DOUBLE NULL,
  `month_loan` DOUBLE NULL,
  `month_total` DOUBLE NULL,
  `fiscalyear` VARCHAR(255) NULL,
  `fiscalyear_grant` DOUBLE NULL,
  `fiscalyear_loan` DOUBLE NULL,
  `fiscalyear_total` DOUBLE NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_designations` (
  `designation_id` BIGINT NOT NULL PRIMARY KEY,
  `designation_code` VARCHAR(255) NULL,
  `designation_name` VARCHAR(255) NULL,
  `designation_slug` VARCHAR(255) NULL,
  `designation_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_donors` (
  `donor_id` BIGINT NOT NULL PRIMARY KEY,
  `donor_code` VARCHAR(255) NULL,
  `donor_name` VARCHAR(255) NULL,
  `donor_slug` VARCHAR(255) NULL,
  `donor_color` VARCHAR(255) NULL,
  `donor_logo` VARCHAR(255) NULL,
  `donor_type` BIGINT NULL,
  `donor_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_executingagencies` (
  `executingagency_id` BIGINT NOT NULL PRIMARY KEY,
  `executingagency_code` VARCHAR(255) NULL,
  `executingagency_name` VARCHAR(255) NULL,
  `executingagency_slug` VARCHAR(255) NULL,
  `executingagency_status` BIGINT NULL,
  `type` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_faqs` (
  `faq_id` BIGINT NOT NULL PRIMARY KEY,
  `module_id` BIGINT NULL,
  `modulelink_id` BIGINT NULL,
  `faq_code` VARCHAR(255) NULL,
  `faq_name` VARCHAR(255) NULL,
  `faq_details` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_faqs_module_id` (`module_id`),
  KEY `ix_wq_faqs_modulelink_id` (`modulelink_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_financialterms` (
  `financialterm_id` BIGINT NOT NULL PRIMARY KEY,
  `wing_id` BIGINT NULL,
  `modalitytype_id` BIGINT NULL,
  `financialterm_code` VARCHAR(255) NULL,
  `financialterm_name` VARCHAR(255) NULL,
  `financialterm_status` BIGINT NULL,
  `financialterm_value` VARCHAR(255) NULL,
  `financial_priority` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_financialterms_wing_id` (`wing_id`),
  KEY `ix_wq_financialterms_modalitytype_id` (`modalitytype_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_governmentpartners` (
  `governmentpartner_id` BIGINT NOT NULL PRIMARY KEY,
  `governmentpartner_code` VARCHAR(255) NULL,
  `governmentpartner_name` VARCHAR(255) NULL,
  `governmentpartner_slug` VARCHAR(255) NULL,
  `governmentpartner_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_grantsources` (
  `grantsource_id` BIGINT NOT NULL PRIMARY KEY,
  `wing_id` BIGINT NULL,
  `grantsource_code` VARCHAR(255) NULL,
  `grantsource_name` VARCHAR(255) NULL,
  `grantsource_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_grantsources_wing_id` (`wing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_implementingunits` (
  `implementingunit_id` BIGINT NOT NULL PRIMARY KEY,
  `implementingunit_code` VARCHAR(255) NULL,
  `implementingunit_name` VARCHAR(255) NULL,
  `implementingunit_slug` VARCHAR(255) NULL,
  `implementingunit_logo` VARCHAR(255) NULL,
  `implementingunit_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_jmccommissions` (
  `jmccommission_id` BIGINT NOT NULL PRIMARY KEY,
  `jmccommission_name` VARCHAR(255) NULL,
  `jmccommission_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_jmccountries` (
  `country_id` BIGINT NOT NULL PRIMARY KEY,
  `country_code` VARCHAR(255) NULL,
  `country_name` VARCHAR(255) NULL,
  `country_slug` VARCHAR(255) NULL,
  `country_type` VARCHAR(255) NULL,
  `country_color` VARCHAR(255) NULL,
  `country_grade` VARCHAR(255) NULL,
  `established_on` VARCHAR(255) NULL,
  `country_details` VARCHAR(255) NULL,
  `country_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_jmcministries` (
  `ministry_id` BIGINT NOT NULL PRIMARY KEY,
  `ministry_code` VARCHAR(255) NULL,
  `ministry_name` VARCHAR(255) NULL,
  `ministry_slug` VARCHAR(255) NULL,
  `ministry_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_jmcsessions` (
  `session_id` BIGINT NOT NULL PRIMARY KEY,
  `session_code` VARCHAR(255) NULL,
  `country_id` BIGINT NULL,
  `session_title` VARCHAR(255) NULL,
  `session_slug` VARCHAR(255) NULL,
  `session_type` BIGINT NULL,
  `session_venue` VARCHAR(255) NULL,
  `latitude` VARCHAR(255) NULL,
  `longitude` VARCHAR(255) NULL,
  `holding_date` VARCHAR(255) NULL,
  `proposed_date` VARCHAR(255) NULL,
  `technical_date` VARCHAR(255) NULL,
  `co_chair_ourside` VARCHAR(255) NULL,
  `co_chair_countryside` VARCHAR(255) NULL,
  `session_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_jmcsessions_country_id` (`country_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_modalitytypes` (
  `modalitytype_id` BIGINT NOT NULL PRIMARY KEY,
  `projecttype_id` BIGINT NULL,
  `wing_id` BIGINT NULL,
  `modalitytype_code` VARCHAR(255) NULL,
  `modalitytype_name` VARCHAR(255) NULL,
  `modalitytype_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_modalitytypes_projecttype_id` (`projecttype_id`),
  KEY `ix_wq_modalitytypes_wing_id` (`wing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_module` (
  `module_id` BIGINT NOT NULL PRIMARY KEY,
  `module_code` VARCHAR(255) NULL,
  `module_title` VARCHAR(255) NULL,
  `module_slug` VARCHAR(255) NULL,
  `module_active_icon` VARCHAR(255) NULL,
  `module_inactive_icon` VARCHAR(255) NULL,
  `module_cover` VARCHAR(255) NULL,
  `module_order` BIGINT NULL,
  `module_status` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_otp` (
  `otp_id` BIGINT NOT NULL PRIMARY KEY,
  `user_id` BIGINT NULL,
  `otp_code` VARCHAR(255) NULL,
  `otp_type` VARCHAR(255) NULL,
  `otp_platform` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_otp_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_outcomes` (
  `outcome_id` BIGINT NOT NULL PRIMARY KEY,
  `outcome_code` VARCHAR(255) NULL,
  `outcome_color` VARCHAR(255) NULL,
  `outcome_name` VARCHAR(255) NULL,
  `outcome_short` VARCHAR(255) NULL,
  `outcome_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_projectcategories` (
  `category_id` BIGINT NOT NULL PRIMARY KEY,
  `category_code` VARCHAR(255) NULL,
  `category_name` VARCHAR(255) NULL,
  `category_slug` VARCHAR(255) NULL,
  `category_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_projectmodes` (
  `projectmode_id` BIGINT NOT NULL PRIMARY KEY,
  `projectmode_code` VARCHAR(255) NULL,
  `projectmode_name` VARCHAR(255) NULL,
  `projectmode_slug` VARCHAR(255) NULL,
  `projectmode_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_projectsectors` (
  `projectsector_id` BIGINT NOT NULL PRIMARY KEY,
  `projectsector_code` VARCHAR(255) NULL,
  `projectsector_name` VARCHAR(255) NULL,
  `projectsector_short` VARCHAR(255) NULL,
  `projectsector_slug` VARCHAR(255) NULL,
  `projectsector_color` VARCHAR(255) NULL,
  `projectsector_status` BIGINT NULL,
  `type` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_projectstatuses` (
  `projectstatus_id` BIGINT NOT NULL PRIMARY KEY,
  `projectstatus_code` VARCHAR(255) NULL,
  `projectstatus_name` VARCHAR(255) NULL,
  `projectstatus_slug` VARCHAR(255) NULL,
  `projectstatus_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_projecttypes` (
  `projecttype_id` BIGINT NOT NULL PRIMARY KEY,
  `projecttype_code` VARCHAR(255) NULL,
  `projecttype_name` VARCHAR(255) NULL,
  `projecttype_slug` VARCHAR(255) NULL,
  `projecttype_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_project_issues` (
  `projectissue_id` BIGINT NOT NULL PRIMARY KEY,
  `projectissue_code` VARCHAR(255) NULL,
  `projectissue_name` VARCHAR(255) NULL,
  `projectissue_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_regions` (
  `region_id` BIGINT NOT NULL PRIMARY KEY,
  `region_code` VARCHAR(255) NULL,
  `region_name` VARCHAR(255) NULL,
  `region_slug` VARCHAR(255) NULL,
  `region_color` VARCHAR(255) NULL,
  `region_logo` VARCHAR(255) NULL,
  `region_short` VARCHAR(255) NULL,
  `region_type` BIGINT NULL,
  `region_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_repositories` (
  `repository_id` BIGINT NOT NULL PRIMARY KEY,
  `user_id` BIGINT NULL,
  `wing_id` BIGINT NULL,
  `refrence_code` VARCHAR(255) NULL,
  `repository_type` VARCHAR(255) NULL,
  `repository_title` VARCHAR(255) NULL,
  `repository_file` VARCHAR(255) NULL,
  `repository_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_repositories_user_id` (`user_id`),
  KEY `ix_wq_repositories_wing_id` (`wing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_role` (
  `role_id` BIGINT NOT NULL PRIMARY KEY,
  `role_code` VARCHAR(255) NULL,
  `role_uuid` VARCHAR(255) NULL,
  `role_title` VARCHAR(255) NULL,
  `role_slug` VARCHAR(255) NULL,
  `role_description` VARCHAR(255) NULL,
  `role_status` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_sdgs` (
  `sdg_id` BIGINT NOT NULL PRIMARY KEY,
  `sdg_code` VARCHAR(255) NULL,
  `sdg_name` VARCHAR(255) NULL,
  `sdg_shortname` VARCHAR(255) NULL,
  `sdg_color` VARCHAR(255) NULL,
  `sdg_avatar` VARCHAR(255) NULL,
  `sdg_order` VARCHAR(255) NULL,
  `sdg_slug` VARCHAR(255) NULL,
  `sdg_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_servicecadres` (
  `servicecadre_id` BIGINT NOT NULL PRIMARY KEY,
  `servicecadre_name` VARCHAR(255) NULL,
  `servicecadre_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_sopapprovals` (
  `sopapproval_id` BIGINT NOT NULL PRIMARY KEY,
  `user_id` BIGINT NULL,
  `wing_id` BIGINT NULL,
  `sopapproval_uuid` VARCHAR(255) NULL,
  `sopapproval_name` VARCHAR(255) NULL,
  `sopapproval_code` VARCHAR(255) NULL,
  `sopapproval_remarks` VARCHAR(255) NULL,
  `sopapproval_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_sopapprovals_user_id` (`user_id`),
  KEY `ix_wq_sopapprovals_wing_id` (`wing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_sponseragencies` (
  `sponseragency_id` BIGINT NOT NULL PRIMARY KEY,
  `sponseragency_code` VARCHAR(255) NULL,
  `sponseragency_name` VARCHAR(255) NULL,
  `sponseragency_slug` VARCHAR(255) NULL,
  `sponseragency_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_tasks` (
  `task_id` BIGINT NOT NULL PRIMARY KEY,
  `task_uuid` VARCHAR(255) NULL,
  `task_code` VARCHAR(255) NULL,
  `task_name` VARCHAR(255) NULL,
  `task_description` VARCHAR(255) NULL,
  `task_deadline` VARCHAR(255) NULL,
  `task_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_timeperiods` (
  `timeperiod_id` BIGINT NOT NULL PRIMARY KEY,
  `timeperiod_code` VARCHAR(255) NULL,
  `timeperiod_name` VARCHAR(255) NULL,
  `timeperiod_slug` VARCHAR(255) NULL,
  `timeperiod_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_users` (
  `user_id` BIGINT NOT NULL PRIMARY KEY,
  `user_uuid` VARCHAR(255) NULL,
  `user_code` VARCHAR(255) NULL,
  `user_fullname` VARCHAR(255) NULL,
  `user_name` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `_verified` BIGINT NULL,
  `_banned` BIGINT NULL,
  `user_type` BIGINT NULL,
  `action_type` BIGINT NULL,
  `user_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_projects` (
  `project_id` BIGINT NOT NULL PRIMARY KEY,
  `project_uuid` VARCHAR(255) NULL,
  `project_code` VARCHAR(255) NULL,
  `project_codeid` VARCHAR(255) NULL,
  `project_name` VARCHAR(255) NULL,
  `project_slug` VARCHAR(255) NULL,
  `project_start` VARCHAR(255) NULL,
  `project_closing` VARCHAR(255) NULL,
  `project_effectiveness` VARCHAR(255) NULL,
  `project_accountopen` BIGINT NULL,
  `project_extended_closing` VARCHAR(255) NULL,
  `project_wayforward` VARCHAR(255) NULL,
  `project_scope` VARCHAR(255) NULL,
  `project_description` VARCHAR(255) NULL,
  `action_so` BIGINT NULL,
  `action_ds` BIGINT NULL,
  `action_js` BIGINT NULL,
  `project_nature` BIGINT NULL,
  `project_satisfactory` BIGINT NULL,
  `project_status` BIGINT NULL,
  `created_by` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_piplineprojects` (
  `piplineproject_id` BIGINT NOT NULL PRIMARY KEY,
  `piplineproject_uuid` VARCHAR(255) NULL,
  `piplineproject_code` VARCHAR(255) NULL,
  `projecttype_id` BIGINT NULL,
  `projectsector_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `piplineproject_name` VARCHAR(255) NULL,
  `piplineproject_slug` VARCHAR(255) NULL,
  `piplineproject_cost` DOUBLE NULL,
  `exchange_rate` BIGINT NULL,
  `piplineproject_costpkr` BIGINT NULL,
  `piplineproject_costusd` BIGINT NULL,
  `piplineproject_description` VARCHAR(255) NULL,
  `loan_type` VARCHAR(255) NULL,
  `cy_wise` DOUBLE NULL,
  `cy_wise_usd` DOUBLE NULL,
  `fy_wise` DOUBLE NULL,
  `fy_wise_usd` DOUBLE NULL,
  `fy_approval_quarter` DOUBLE NULL,
  `fy_approval_quarter_usd` DOUBLE NULL,
  `piplineproject_status` BIGINT NULL,
  `loan_amount` DOUBLE NULL,
  `loan_amount_usd` DOUBLE NULL,
  `loan_amount_type` VARCHAR(255) NULL,
  `grant_amount` DOUBLE NULL,
  `grant_amount_usd` DOUBLE NULL,
  `grant_amount_type` VARCHAR(255) NULL,
  `gurantee` VARCHAR(255) NULL,
  `gurantee_type` VARCHAR(255) NULL,
  `gurantee_usd` VARCHAR(255) NULL,
  `pipline_year` VARCHAR(255) NULL,
  `approval_year` VARCHAR(255) NULL,
  `approval_quarter` VARCHAR(255) NULL,
  `ocr_amount_type` VARCHAR(255) NULL,
  `ocr_amount` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_piplineprojects_projecttype_id` (`projecttype_id`),
  KEY `ix_wq_piplineprojects_projectsector_id` (`projectsector_id`),
  KEY `ix_wq_piplineprojects_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_programs` (
  `program_id` BIGINT NOT NULL PRIMARY KEY,
  `program_uuid` VARCHAR(255) NULL,
  `program_code` VARCHAR(255) NULL,
  `program_name` VARCHAR(255) NULL,
  `program_slug` VARCHAR(255) NULL,
  `currency_id` BIGINT NULL,
  `implementing_agency` VARCHAR(255) NULL,
  `program_cost` DOUBLE NULL,
  `exchange_rate` DOUBLE NULL,
  `program_costpkr` DOUBLE NULL,
  `program_costusd` DOUBLE NULL,
  `program_disbursement` DOUBLE NULL,
  `program_financingterms` VARCHAR(255) NULL,
  `program_sign` VARCHAR(255) NULL,
  `program_closing` VARCHAR(255) NULL,
  `program_description` VARCHAR(255) NULL,
  `program_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_wq_programs_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wq_offbudgets` (
  `offbudget_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_uuid` VARCHAR(255) NULL,
  `offbudget_codeid` VARCHAR(255) NULL,
  `offbudget_code` VARCHAR(255) NULL,
  `offbudget_name` VARCHAR(255) NULL,
  `offbudget_implementation` BIGINT NULL,
  `offbudget_slug` VARCHAR(255) NULL,
  `offbudget_start` VARCHAR(255) NULL,
  `offbudget_end` VARCHAR(255) NULL,
  `offbudget_outcomes` VARCHAR(255) NULL,
  `offbudget_objectives` VARCHAR(255) NULL,
  `offbudget_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `cache` (
  `key` BIGINT NULL,
  `value` VARCHAR(255) NULL,
  `expiration` BIGINT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `cache_locks` (
  `key` BIGINT NULL,
  `owner` VARCHAR(255) NULL,
  `expiration` BIGINT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `course_to_applicants` (
  `to_applicantid` BIGINT NULL,
  `course_id` BIGINT NULL,
  `region_id` BIGINT NULL,
  `applicant_name` VARCHAR(255) NULL,
  `applicant_dob` VARCHAR(255) NULL,
  `applicant_passport` VARCHAR(255) NULL,
  `applicant_responsiblity` VARCHAR(255) NULL,
  `applicant_grade` VARCHAR(255) NULL,
  `applicant_education` VARCHAR(255) NULL,
  `applicant_degree` VARCHAR(255) NULL,
  `applicant_probation` BIGINT NULL,
  `applicant_blacklist` BIGINT NULL,
  `applicant_joining` VARCHAR(255) NULL,
  `applicant_scale` VARCHAR(255) NULL,
  `applicant_department` VARCHAR(255) NULL,
  `applicant_designation` VARCHAR(255) NULL,
  `applicant_cnic` VARCHAR(255) NULL,
  `applicant_cadre` VARCHAR(255) NULL,
  `applicant_gender` BIGINT NULL,
  `applicant_type` BIGINT NULL,
  `applicant_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_course_to_applicants_course_id` (`course_id`),
  KEY `ix_course_to_applicants_region_id` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `course_to_countries` (
  `to_countryid` BIGINT NULL,
  `course_id` BIGINT NULL,
  `country_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_course_to_countries_course_id` (`course_id`),
  KEY `ix_course_to_countries_country_id` (`country_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `course_to_donors` (
  `to_donorid` BIGINT NULL,
  `course_id` BIGINT NULL,
  `donor_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_course_to_donors_course_id` (`course_id`),
  KEY `ix_course_to_donors_donor_id` (`donor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `course_to_executingagencies` (
  `to_executingagencyid` BIGINT NULL,
  `course_id` BIGINT NULL,
  `executingagency_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_course_to_executingagencies_course_id` (`course_id`),
  KEY `ix_course_to_executingagencies_executingagency_id` (`executingagency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `course_to_sectors` (
  `to_sectorid` BIGINT NULL,
  `course_id` BIGINT NULL,
  `sector_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_course_to_sectors_course_id` (`course_id`),
  KEY `ix_course_to_sectors_sector_id` (`sector_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `course_to_sponseragencies` (
  `to_sponseragenyid` BIGINT NULL,
  `course_id` BIGINT NULL,
  `sponseragency_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_course_to_sponseragencies_course_id` (`course_id`),
  KEY `ix_course_to_sponseragencies_sponseragency_id` (`sponseragency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `donor_to_types` (
  `todonor_id` BIGINT NOT NULL PRIMARY KEY,
  `donor_id` BIGINT NULL,
  `type` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_donor_to_types_donor_id` (`donor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `failed_jobs` (
  `id` BIGINT NOT NULL PRIMARY KEY,
  `uuid` VARCHAR(255) NULL,
  `connection` VARCHAR(255) NULL,
  `queue` VARCHAR(255) NULL,
  `payload` VARCHAR(255) NULL,
  `exception` VARCHAR(255) NULL,
  `failed_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `faqs_to_attachments` (
  `faqattachment_id` BIGINT NOT NULL PRIMARY KEY,
  `faq_id` BIGINT NULL,
  `attachment_name` VARCHAR(255) NULL,
  `attachment_file` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_faqs_to_attachments_faq_id` (`faq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `faqs_to_videos` (
  `faqvideo_id` BIGINT NOT NULL PRIMARY KEY,
  `faq_id` BIGINT NULL,
  `video_name` VARCHAR(255) NULL,
  `video_file` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_faqs_to_videos_faq_id` (`faq_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmccountires_to_areas` (
  `area_id` BIGINT NOT NULL PRIMARY KEY,
  `country_id` BIGINT NULL,
  `area_name` VARCHAR(255) NULL,
  `area_slug` VARCHAR(255) NULL,
  `area_code` VARCHAR(255) NULL,
  `area_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmccountires_to_areas_country_id` (`country_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmccountires_to_cochairs` (
  `cochair_id` BIGINT NOT NULL PRIMARY KEY,
  `country_id` BIGINT NULL,
  `cochair_ourside` VARCHAR(255) NULL,
  `cochair_countryside` VARCHAR(255) NULL,
  `cochair_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmccountires_to_cochairs_country_id` (`country_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmccountry_to_traders` (
  `totrade_id` BIGINT NOT NULL PRIMARY KEY,
  `country_id` BIGINT NULL,
  `year` VARCHAR(255) NULL,
  `export` VARCHAR(255) NULL,
  `import` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmccountry_to_traders_country_id` (`country_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_agendas` (
  `to_agendaid` BIGINT NULL,
  `ministry_id` BIGINT NULL,
  `session_id` BIGINT NULL,
  `agenda_heading` VARCHAR(255) NULL,
  `agenda_details` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_agendas_ministry_id` (`ministry_id`),
  KEY `ix_jmcsession_to_agendas_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_draftprotocols` (
  `to_draftprotocolid` BIGINT NULL,
  `session_id` BIGINT NULL,
  `ministry_id` BIGINT NULL,
  `draftprotocol_title` VARCHAR(255) NULL,
  `draftprotocol_draftby` VARCHAR(255) NULL,
  `draftprotocol_date` VARCHAR(255) NULL,
  `draftprotocol_heading` VARCHAR(255) NULL,
  `draftprotocol_details` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_draftprotocols_session_id` (`session_id`),
  KEY `ix_jmcsession_to_draftprotocols_ministry_id` (`ministry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_immfiles` (
  `immfile_id` BIGINT NOT NULL PRIMARY KEY,
  `to_immid` BIGINT NULL,
  `session_id` BIGINT NULL,
  `label` VARCHAR(255) NULL,
  `attachment` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_immfiles_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_immrenminders` (
  `to_immreminderid` BIGINT NULL,
  `to_immid` BIGINT NULL,
  `session_id` BIGINT NULL,
  `ministry_id` BIGINT NULL,
  `reminder_title` VARCHAR(255) NULL,
  `reminder_details` VARCHAR(255) NULL,
  `reminder_deadline` VARCHAR(255) NULL,
  `reminder_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_immrenminders_session_id` (`session_id`),
  KEY `ix_jmcsession_to_immrenminders_ministry_id` (`ministry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_imms` (
  `to_immid` BIGINT NULL,
  `session_id` BIGINT NULL,
  `imm_title` VARCHAR(255) NULL,
  `imm_type` VARCHAR(255) NULL,
  `imm_venue` VARCHAR(255) NULL,
  `imm_date` VARCHAR(255) NULL,
  `imm_time` VARCHAR(255) NULL,
  `imm_chair` VARCHAR(255) NULL,
  `imm_attachments` VARCHAR(255) NULL,
  `imm_minutes` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_imms_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_implementations` (
  `toimplementation_id` BIGINT NOT NULL PRIMARY KEY,
  `session_id` BIGINT NULL,
  `ministry_id` BIGINT NULL,
  `to_draftprotocolid` BIGINT NULL,
  `implementation_status` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_implementations_session_id` (`session_id`),
  KEY `ix_jmcsession_to_implementations_ministry_id` (`ministry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_jmccountries` (
  `to_jmccountryid` BIGINT NULL,
  `session_id` BIGINT NULL,
  `country_id` BIGINT NULL,
  `area_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_jmccountries_session_id` (`session_id`),
  KEY `ix_jmcsession_to_jmccountries_country_id` (`country_id`),
  KEY `ix_jmcsession_to_jmccountries_area_id` (`area_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_proposalfiles` (
  `proposalfile_id` BIGINT NOT NULL PRIMARY KEY,
  `to_proposalid` BIGINT NULL,
  `session_id` BIGINT NULL,
  `label` VARCHAR(255) NULL,
  `attachment` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_proposalfiles_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_proposals` (
  `to_proposalid` BIGINT NULL,
  `session_id` BIGINT NULL,
  `request_id` BIGINT NULL,
  `proposal_title` VARCHAR(255) NULL,
  `proposal_details` VARCHAR(255) NULL,
  `proposal_attachment` VARCHAR(255) NULL,
  `person_name` VARCHAR(255) NULL,
  `person_email` VARCHAR(255) NULL,
  `person_contact` VARCHAR(255) NULL,
  `person_designation` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_proposals_session_id` (`session_id`),
  KEY `ix_jmcsession_to_proposals_request_id` (`request_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_requestfiles` (
  `requestfile_id` BIGINT NOT NULL PRIMARY KEY,
  `request_id` BIGINT NULL,
  `session_id` BIGINT NULL,
  `label` VARCHAR(255) NULL,
  `attachment` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_requestfiles_request_id` (`request_id`),
  KEY `ix_jmcsession_to_requestfiles_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_requestministries` (
  `requestministry_id` BIGINT NOT NULL PRIMARY KEY,
  `request_id` BIGINT NULL,
  `session_id` BIGINT NULL,
  `ministry_id` BIGINT NULL,
  `status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_requestministries_request_id` (`request_id`),
  KEY `ix_jmcsession_to_requestministries_session_id` (`session_id`),
  KEY `ix_jmcsession_to_requestministries_ministry_id` (`ministry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_requests` (
  `request_id` BIGINT NOT NULL PRIMARY KEY,
  `session_id` BIGINT NULL,
  `ministry_id` BIGINT NULL,
  `request_title` VARCHAR(255) NULL,
  `request_details` VARCHAR(255) NULL,
  `request_deadline` VARCHAR(255) NULL,
  `request_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_requests_session_id` (`session_id`),
  KEY `ix_jmcsession_to_requests_ministry_id` (`ministry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmcsession_to_signedprotocols` (
  `to_signedprotocolid` BIGINT NULL,
  `session_id` BIGINT NULL,
  `protocol_title` VARCHAR(255) NULL,
  `protocol_date` VARCHAR(255) NULL,
  `protocol_signedby` VARCHAR(255) NULL,
  `protocol_details` VARCHAR(255) NULL,
  `protocol_summary` VARCHAR(255) NULL,
  `protocol_attachment` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmcsession_to_signedprotocols_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmc_logs` (
  `jmclog_id` BIGINT NOT NULL PRIMARY KEY,
  `session_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `component_name` VARCHAR(255) NULL,
  `component_data` VARCHAR(255) NULL,
  `jmclog_json` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmc_logs_session_id` (`session_id`),
  KEY `ix_jmc_logs_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jmc_to_technical_sessions` (
  `technicalsession_id` BIGINT NOT NULL PRIMARY KEY,
  `head_ourside` VARCHAR(255) NULL,
  `head_countryside` VARCHAR(255) NULL,
  `session_id` BIGINT NULL,
  `ministries` VARCHAR(255) NULL,
  `attachment` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_jmc_to_technical_sessions_session_id` (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `jobs` (
  `id` BIGINT NOT NULL PRIMARY KEY,
  `queue` VARCHAR(255) NULL,
  `payload` VARCHAR(255) NULL,
  `attempts` BIGINT NULL,
  `reserved_at` BIGINT NULL,
  `available_at` BIGINT NULL,
  `created_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `job_batches` (
  `id` BIGINT NOT NULL PRIMARY KEY,
  `name` VARCHAR(255) NULL,
  `total_jobs` BIGINT NULL,
  `pending_jobs` BIGINT NULL,
  `failed_jobs` BIGINT NULL,
  `failed_job_ids` VARCHAR(255) NULL,
  `options` VARCHAR(255) NULL,
  `cancelled_at` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `finished_at` BIGINT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `migrations` (
  `id` BIGINT NOT NULL PRIMARY KEY,
  `migration` VARCHAR(255) NULL,
  `batch` BIGINT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `module_to_links` (
  `modulelink_id` BIGINT NOT NULL PRIMARY KEY,
  `module_id` BIGINT NULL,
  `parent_id` BIGINT NULL,
  `modulelink_code` VARCHAR(255) NULL,
  `link_title` VARCHAR(255) NULL,
  `link_val` VARCHAR(255) NULL,
  `link_order` BIGINT NULL,
  `_visibility` BIGINT NULL,
  `icon` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_module_to_links_module_id` (`module_id`),
  KEY `ix_module_to_links_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `notifications` (
  `id` BIGINT NOT NULL PRIMARY KEY,
  `type` VARCHAR(255) NULL,
  `notifiable_type` VARCHAR(255) NULL,
  `notifiable_id` BIGINT NULL,
  `data` VARCHAR(255) NULL,
  `read_at` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_notifications_notifiable_id` (`notifiable_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_challengs` (
  `tochalleng_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `challeng_id` BIGINT NULL,
  `issue_text` VARCHAR(255) NULL,
  `way_forward` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_challengs_offbudget_id` (`offbudget_id`),
  KEY `ix_offbudget_to_challengs_challeng_id` (`challeng_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_disbursments` (
  `todisbursment_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `disbursement_type` VARCHAR(255) NULL,
  `currency_id` BIGINT NULL,
  `amount` VARCHAR(255) NULL,
  `exchangerate_usd` VARCHAR(255) NULL,
  `amount_usd` VARCHAR(255) NULL,
  `date` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_disbursments_offbudget_id` (`offbudget_id`),
  KEY `ix_offbudget_to_disbursments_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_donors` (
  `todonor_id` BIGINT NOT NULL PRIMARY KEY,
  `donor_id` BIGINT NULL,
  `offbudget_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `type` VARCHAR(255) NULL,
  `amount` VARCHAR(255) NULL,
  `exchangerate_usd` VARCHAR(255) NULL,
  `amount_usd` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_donors_donor_id` (`donor_id`),
  KEY `ix_offbudget_to_donors_offbudget_id` (`offbudget_id`),
  KEY `ix_offbudget_to_donors_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_executingagencies` (
  `toexecutingagency_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `executingagency_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_executingagencies_offbudget_id` (`offbudget_id`),
  KEY `ix_offbudget_to_executingagencies_executingagency_id` (`executingagency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_financials` (
  `tofinancial_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `amount` VARCHAR(255) NULL,
  `amount_pkr` VARCHAR(255) NULL,
  `amount_usd` VARCHAR(255) NULL,
  `exchangerate_usd` BIGINT NULL,
  `exchangerate_pkr` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_financials_offbudget_id` (`offbudget_id`),
  KEY `ix_offbudget_to_financials_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_governmentpartners` (
  `togovernmentpartner_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `governmentpartner_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_governmentpartners_offbudget_id` (`offbudget_id`),
  KEY `ix_offbudget_to_governmentpartners_governmentpartner_id` (`governmentpartner_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_outcomes` (
  `offbudgetoutcome_id` BIGINT NOT NULL PRIMARY KEY,
  `outcome_id` BIGINT NULL,
  `offbudget_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_outcomes_outcome_id` (`outcome_id`),
  KEY `ix_offbudget_to_outcomes_offbudget_id` (`offbudget_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_regions` (
  `toregion_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `region_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_regions_offbudget_id` (`offbudget_id`),
  KEY `ix_offbudget_to_regions_region_id` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_remarks` (
  `toremarks_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `remarks` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_remarks_offbudget_id` (`offbudget_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `offbudget_to_sdgs` (
  `tosdg_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `sdg_id` BIGINT NULL,
  `remarks` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_offbudget_to_sdgs_offbudget_id` (`offbudget_id`),
  KEY `ix_offbudget_to_sdgs_sdg_id` (`sdg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `password_reset_tokens` (
  `email` BIGINT NULL,
  `token` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `personal_access_tokens` (
  `id` BIGINT NOT NULL PRIMARY KEY,
  `tokenable_type` VARCHAR(255) NULL,
  `tokenable_id` BIGINT NULL,
  `name` VARCHAR(255) NULL,
  `token` VARCHAR(255) NULL,
  `abilities` VARCHAR(255) NULL,
  `last_used_at` VARCHAR(255) NULL,
  `expires_at` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_personal_access_tokens_tokenable_id` (`tokenable_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `piplineprojects_to_approvalforums` (
  `to_approvalforumid` BIGINT NULL,
  `piplineproject_id` BIGINT NULL,
  `approvalforum_id` BIGINT NULL,
  `approvalforum_date` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_piplineprojects_to_approvalforums_piplineproject_id` (`piplineproject_id`),
  KEY `ix_piplineprojects_to_approvalforums_approvalforum_id` (`approvalforum_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `piplineprojects_to_donors` (
  `todonor_id` BIGINT NOT NULL PRIMARY KEY,
  `piplineproject_id` BIGINT NULL,
  `donor_id` BIGINT NULL,
  `type` VARCHAR(255) NULL,
  `terms` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_piplineprojects_to_donors_piplineproject_id` (`piplineproject_id`),
  KEY `ix_piplineprojects_to_donors_donor_id` (`donor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `piplineprojects_to_regions` (
  `to_regionid` BIGINT NULL,
  `piplineproject_id` BIGINT NULL,
  `region_id` BIGINT NULL,
  `latitude` VARCHAR(255) NULL,
  `longitude` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_piplineprojects_to_regions_piplineproject_id` (`piplineproject_id`),
  KEY `ix_piplineprojects_to_regions_region_id` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `piplineproject_logs` (
  `piplineprojectlog_id` BIGINT NOT NULL PRIMARY KEY,
  `piplineproject_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `component_name` VARCHAR(255) NULL,
  `component_data` VARCHAR(255) NULL,
  `pipelineproject_json` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_piplineproject_logs_piplineproject_id` (`piplineproject_id`),
  KEY `ix_piplineproject_logs_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `piplineproject_to_wings` (
  `piplineprojecttowings_id` BIGINT NOT NULL PRIMARY KEY,
  `piplineproject_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `wing_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_piplineproject_to_wings_piplineproject_id` (`piplineproject_id`),
  KEY `ix_piplineproject_to_wings_user_id` (`user_id`),
  KEY `ix_piplineproject_to_wings_wing_id` (`wing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `pipline_to_donorterms` (
  `toterm_id` BIGINT NOT NULL PRIMARY KEY,
  `piplineproject_id` BIGINT NULL,
  `todonor_id` BIGINT NULL,
  `financialterm_id` BIGINT NULL,
  `financialterm_value` BIGINT NULL,
  `modality_type` BIGINT NULL,
  `repayment_date` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_pipline_to_donorterms_piplineproject_id` (`piplineproject_id`),
  KEY `ix_pipline_to_donorterms_todonor_id` (`todonor_id`),
  KEY `ix_pipline_to_donorterms_financialterm_id` (`financialterm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `pipline_to_projecttypes` (
  `to_piplineprojecttype_id` BIGINT NOT NULL PRIMARY KEY,
  `piplineproject_id` BIGINT NULL,
  `projecttype_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `amount` VARCHAR(255) NULL,
  `exchange_rate` VARCHAR(255) NULL,
  `amount_usd` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_pipline_to_projecttypes_piplineproject_id` (`piplineproject_id`),
  KEY `ix_pipline_to_projecttypes_projecttype_id` (`projecttype_id`),
  KEY `ix_pipline_to_projecttypes_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_logs` (
  `programlog_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `component_name` VARCHAR(255) NULL,
  `component_data` VARCHAR(255) NULL,
  `programlog_json` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_logs_program_id` (`program_id`),
  KEY `ix_program_logs_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_to_approvalforums` (
  `toapprovalforum_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `approvalforum_id` BIGINT NULL,
  `approvalforum_date` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_to_approvalforums_program_id` (`program_id`),
  KEY `ix_program_to_approvalforums_approvalforum_id` (`approvalforum_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_to_donors` (
  `todonor_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `donor_id` BIGINT NULL,
  `type` VARCHAR(255) NULL,
  `terms` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_to_donors_program_id` (`program_id`),
  KEY `ix_program_to_donors_donor_id` (`donor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_to_donorterms` (
  `toterm_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `todonor_id` BIGINT NULL,
  `financialterm_id` BIGINT NULL,
  `financialterm_value` BIGINT NULL,
  `modality_type` BIGINT NULL,
  `repayment_date` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_to_donorterms_program_id` (`program_id`),
  KEY `ix_program_to_donorterms_todonor_id` (`todonor_id`),
  KEY `ix_program_to_donorterms_financialterm_id` (`financialterm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_to_executinagencies` (
  `toexecutingagency_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `executingagency_id` BIGINT NULL,
  `terms` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_to_executinagencies_program_id` (`program_id`),
  KEY `ix_program_to_executinagencies_executingagency_id` (`executingagency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_to_regions` (
  `toregion_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `region_id` BIGINT NULL,
  `latitude` VARCHAR(255) NULL,
  `longitude` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_to_regions_program_id` (`program_id`),
  KEY `ix_program_to_regions_region_id` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_to_sectors` (
  `tosector_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `projectsector_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_to_sectors_program_id` (`program_id`),
  KEY `ix_program_to_sectors_projectsector_id` (`projectsector_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_to_sponseragencies` (
  `tosponseragency_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `sponseragency_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_to_sponseragencies_program_id` (`program_id`),
  KEY `ix_program_to_sponseragencies_sponseragency_id` (`sponseragency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `program_to_wings` (
  `programtowings_id` BIGINT NOT NULL PRIMARY KEY,
  `program_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `wing_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_program_to_wings_program_id` (`program_id`),
  KEY `ix_program_to_wings_user_id` (`user_id`),
  KEY `ix_program_to_wings_wing_id` (`wing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `projectsector_to_subsectors` (
  `subsector_id` BIGINT NOT NULL PRIMARY KEY,
  `projectsector_id` BIGINT NULL,
  `subsector_code` VARCHAR(255) NULL,
  `subsector_name` VARCHAR(255) NULL,
  `subsector_color` VARCHAR(255) NULL,
  `subsector_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_projectsector_to_subsectors_projectsector_id` (`projectsector_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_logs` (
  `projectlog_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `component_name` VARCHAR(255) NULL,
  `component_data` VARCHAR(255) NULL,
  `projectlog_json` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_logs_project_id` (`project_id`),
  KEY `ix_project_logs_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_approvalforums` (
  `projecttoapprovalforum_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `approvalforum_id` BIGINT NULL,
  `approvalforum_date` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_approvalforums_project_id` (`project_id`),
  KEY `ix_project_to_approvalforums_approvalforum_id` (`approvalforum_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_categories` (
  `projecttocategory_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `category_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_categories_project_id` (`project_id`),
  KEY `ix_project_to_categories_category_id` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_disbursementdetails` (
  `projectdisbursementdetail_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `projectdisbursement_id` BIGINT NULL,
  `timeperiod_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `sum_type` VARCHAR(255) NULL,
  `detail_type` VARCHAR(255) NULL,
  `from` VARCHAR(255) NULL,
  `to` VARCHAR(255) NULL,
  `amount` VARCHAR(255) NULL,
  `amount_usd` VARCHAR(255) NULL,
  `exchangerate_usd` DOUBLE NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_disbursementdetails_project_id` (`project_id`),
  KEY `ix_project_to_disbursementdetails_projectdisbursement_id` (`projectdisbursement_id`),
  KEY `ix_project_to_disbursementdetails_timeperiod_id` (`timeperiod_id`),
  KEY `ix_project_to_disbursementdetails_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_disbursements` (
  `projectdisbursement_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `disbursement_type` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_disbursements_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_executingencies` (
  `projecttoexecutingency_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `executingagency_id` BIGINT NULL,
  `region_id` BIGINT NULL,
  `latitude` VARCHAR(255) NULL,
  `longitude` VARCHAR(255) NULL,
  `pd_name` VARCHAR(255) NULL,
  `pd_email` VARCHAR(255) NULL,
  `pd_contact` VARCHAR(255) NULL,
  `implementing_unit` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_executingencies_project_id` (`project_id`),
  KEY `ix_project_to_executingencies_executingagency_id` (`executingagency_id`),
  KEY `ix_project_to_executingencies_region_id` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_extentions` (
  `projecttoextention_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `extension_label` VARCHAR(255) NULL,
  `extension_date` VARCHAR(255) NULL,
  `extension_remarks` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_extentions_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_financialdistributions` (
  `financialdistribution_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `region_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `amount` VARCHAR(255) NULL,
  `amount_usd` VARCHAR(255) NULL,
  `exchange_rate` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_financialdistributions_project_id` (`project_id`),
  KEY `ix_project_to_financialdistributions_region_id` (`region_id`),
  KEY `ix_project_to_financialdistributions_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_financials` (
  `projecttofinancial_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `projectcost_currency` BIGINT NULL,
  `project_cost` DOUBLE NULL,
  `projectcost_exchange` DOUBLE NULL,
  `projectcost_usdexchange` DOUBLE NULL,
  `projectcost_pkr` DOUBLE NULL,
  `projectcost_usd` DOUBLE NULL,
  `loan_amount` DOUBLE NULL,
  `loan_amountusd` DOUBLE NULL,
  `loan_currency` BIGINT NULL,
  `loan_id` VARCHAR(255) NULL,
  `grant_amount` DOUBLE NULL,
  `grant_amountusd` DOUBLE NULL,
  `grant_currency` BIGINT NULL,
  `grand_id` VARCHAR(255) NULL,
  `local_component` DOUBLE NULL,
  `financial_close` BIGINT NULL,
  `local_componentcurrency` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_financials_project_id` (`project_id`),
  KEY `ix_project_to_financials_loan_id` (`loan_id`),
  KEY `ix_project_to_financials_grand_id` (`grand_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_foreigncecomponents` (
  `projecttoforeigncecomponent_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `donor_id` BIGINT NULL,
  `exchangerate_usd` DOUBLE NULL,
  `loan_currency` BIGINT NULL,
  `loan_amount` DOUBLE NULL,
  `loan_amount_usd` DOUBLE NULL,
  `grant_currency` BIGINT NULL,
  `grant_amount` DOUBLE NULL,
  `grant_amount_usd` DOUBLE NULL,
  `graceperiod_from` VARCHAR(255) NULL,
  `graceperiod_to` VARCHAR(255) NULL,
  `initial_approval` VARCHAR(255) NULL,
  `type` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_foreigncecomponents_project_id` (`project_id`),
  KEY `ix_project_to_foreigncecomponents_donor_id` (`donor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_foreigncecomponentterms` (
  `toterm_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `projecttoforeigndetail_id` BIGINT NULL,
  `financialterm_id` BIGINT NULL,
  `financialterm_value` VARCHAR(255) NULL,
  `modality_type` BIGINT NULL,
  `repayment_date` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_foreigncecomponentterms_project_id` (`project_id`),
  KEY `ix_project_to_foreigncecomponentterms_projecttoforeigndetail_id` (`projecttoforeigndetail_id`),
  KEY `ix_project_to_foreigncecomponentterms_financialterm_id` (`financialterm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_foreigndetails` (
  `projecttoforeigndetail_id` BIGINT NOT NULL PRIMARY KEY,
  `projecttoforeigncecomponent_id` BIGINT NULL,
  `project_id` BIGINT NULL,
  `donor_id` BIGINT NULL,
  `type` VARCHAR(255) NULL,
  `modalitytype_id` BIGINT NULL,
  `grantsource_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `id` VARCHAR(255) NULL,
  `amount` DOUBLE NULL,
  `amount_usd` DOUBLE NULL,
  `exchange_rate` DOUBLE NULL,
  `graceperiod_from` VARCHAR(255) NULL,
  `graceperiod_to` VARCHAR(255) NULL,
  `initial_approval` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_foreigndetails_projecttoforeigncecomponent_id` (`projecttoforeigncecomponent_id`),
  KEY `ix_project_to_foreigndetails_project_id` (`project_id`),
  KEY `ix_project_to_foreigndetails_donor_id` (`donor_id`),
  KEY `ix_project_to_foreigndetails_modalitytype_id` (`modalitytype_id`),
  KEY `ix_project_to_foreigndetails_grantsource_id` (`grantsource_id`),
  KEY `ix_project_to_foreigndetails_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_issues` (
  `toissue_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `projectissue_id` BIGINT NULL,
  `remarks` VARCHAR(255) NULL,
  `wayforward` VARCHAR(255) NULL,
  `issue_order` BIGINT NULL,
  `projectissue_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_issues_project_id` (`project_id`),
  KEY `ix_project_to_issues_projectissue_id` (`projectissue_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_localcomponents` (
  `localcomponent_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `region_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `amount` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_localcomponents_project_id` (`project_id`),
  KEY `ix_project_to_localcomponents_region_id` (`region_id`),
  KEY `ix_project_to_localcomponents_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_parallels` (
  `projectparallel_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `project_parallel` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_parallels_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_physicalprogresses` (
  `projecttophysicalprogress_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `progress_label` VARCHAR(255) NULL,
  `progress_remarks` VARCHAR(255) NULL,
  `from_quarter` VARCHAR(255) NULL,
  `from_year` VARCHAR(255) NULL,
  `to_quarter` VARCHAR(255) NULL,
  `to_year` VARCHAR(255) NULL,
  `progress_completion` VARCHAR(255) NULL,
  `action_taken` VARCHAR(255) NULL,
  `status` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_physicalprogresses_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_projectmodes` (
  `projecttoprojectmode_id` BIGINT NOT NULL PRIMARY KEY,
  `projectmode_id` BIGINT NULL,
  `project_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_projectmodes_projectmode_id` (`projectmode_id`),
  KEY `ix_project_to_projectmodes_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_projectsectors` (
  `projecttoprojectsector_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `projectsector_id` BIGINT NULL,
  `subsector_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `sector_amount` VARCHAR(255) NULL,
  `sector_usdamount` VARCHAR(255) NULL,
  `exchange_rate` DOUBLE NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_projectsectors_project_id` (`project_id`),
  KEY `ix_project_to_projectsectors_projectsector_id` (`projectsector_id`),
  KEY `ix_project_to_projectsectors_subsector_id` (`subsector_id`),
  KEY `ix_project_to_projectsectors_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_projecttypes` (
  `projecttoprojecttype_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `projecttype_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_projecttypes_project_id` (`project_id`),
  KEY `ix_project_to_projecttypes_projecttype_id` (`projecttype_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_regioncosts` (
  `to_regioncostid` BIGINT NULL,
  `project_id` BIGINT NULL,
  `region_id` BIGINT NULL,
  `currency_id` BIGINT NULL,
  `amount` VARCHAR(255) NULL,
  `exchange_rate` VARCHAR(255) NULL,
  `amount_usd` VARCHAR(255) NULL,
  `type` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_regioncosts_project_id` (`project_id`),
  KEY `ix_project_to_regioncosts_region_id` (`region_id`),
  KEY `ix_project_to_regioncosts_currency_id` (`currency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_revisedcosts` (
  `projecttorevisedcost_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `revised_cost` DOUBLE NULL,
  `revisedcost_currency` BIGINT NULL,
  `revisedcost_exchange` DOUBLE NULL,
  `revisedcost_pkr` DOUBLE NULL,
  `revisedcost_usd` DOUBLE NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_revisedcosts_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_revisondates` (
  `projecttorevisondate_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `revision_date` VARCHAR(255) NULL,
  `revision_remarks` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_revisondates_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_scopes` (
  `toscope_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `remarks` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_scopes_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_sponsoragencies` (
  `projecttosponsoragency_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `sponseragency_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_sponsoragencies_project_id` (`project_id`),
  KEY `ix_project_to_sponsoragencies_sponseragency_id` (`sponseragency_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_umbrella` (
  `projectumbrella_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `project_umbrella` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_umbrella_project_id` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `project_to_wings` (
  `projecttowing_id` BIGINT NOT NULL PRIMARY KEY,
  `project_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `wing_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_project_to_wings_project_id` (`project_id`),
  KEY `ix_project_to_wings_user_id` (`user_id`),
  KEY `ix_project_to_wings_wing_id` (`wing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `remark_to_sdgs` (
  `tosdg_id` BIGINT NOT NULL PRIMARY KEY,
  `offbudget_id` BIGINT NULL,
  `toremarks_id` BIGINT NULL,
  `sdg_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_remark_to_sdgs_offbudget_id` (`offbudget_id`),
  KEY `ix_remark_to_sdgs_toremarks_id` (`toremarks_id`),
  KEY `ix_remark_to_sdgs_sdg_id` (`sdg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `role_to_links` (
  `rolelink_id` BIGINT NOT NULL PRIMARY KEY,
  `modulelink_id` BIGINT NULL,
  `role_id` BIGINT NULL,
  `rolelink_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_role_to_links_modulelink_id` (`modulelink_id`),
  KEY `ix_role_to_links_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `role_to_module` (
  `rolemodule_id` BIGINT NOT NULL PRIMARY KEY,
  `role_id` BIGINT NULL,
  `module_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_role_to_module_role_id` (`role_id`),
  KEY `ix_role_to_module_module_id` (`module_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `sessions` (
  `id` BIGINT NOT NULL PRIMARY KEY,
  `user_id` BIGINT NULL,
  `ip_address` VARCHAR(255) NULL,
  `user_agent` VARCHAR(255) NULL,
  `payload` VARCHAR(255) NULL,
  `last_activity` BIGINT NULL,
  KEY `ix_sessions_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `task_mark_to_user` (
  `taskmark_id` BIGINT NOT NULL PRIMARY KEY,
  `task_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `task_deadline` VARCHAR(255) NULL,
  `mark_description` VARCHAR(255) NULL,
  `mark_type` BIGINT NULL,
  `mark_by` BIGINT NULL,
  `action_taken` BIGINT NULL,
  `task_log` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_task_mark_to_user_task_id` (`task_id`),
  KEY `ix_task_mark_to_user_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `task_to_attachments` (
  `taskattachment_id` BIGINT NOT NULL PRIMARY KEY,
  `task_id` BIGINT NULL,
  `taskmark_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `attachment_label` VARCHAR(255) NULL,
  `attachment_file` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_task_to_attachments_task_id` (`task_id`),
  KEY `ix_task_to_attachments_taskmark_id` (`taskmark_id`),
  KEY `ix_task_to_attachments_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `task_to_seen` (
  `task_seenid` BIGINT NULL,
  `task_id` BIGINT NULL,
  `seen_at` VARCHAR(255) NULL,
  `taskmark_id` BIGINT NULL,
  `user_id` BIGINT NULL,
  `seen_status` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_task_to_seen_task_id` (`task_id`),
  KEY `ix_task_to_seen_taskmark_id` (`taskmark_id`),
  KEY `ix_task_to_seen_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user_to_ministries` (
  `usertoministry_id` BIGINT NOT NULL PRIMARY KEY,
  `user_id` BIGINT NULL,
  `ministry_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_user_to_ministries_user_id` (`user_id`),
  KEY `ix_user_to_ministries_ministry_id` (`ministry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user_to_profile` (
  `userprofile_id` BIGINT NOT NULL PRIMARY KEY,
  `user_id` BIGINT NULL,
  `avatar` VARCHAR(255) NULL,
  `contact` VARCHAR(255) NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_user_to_profile_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user_to_role` (
  `userrole_id` BIGINT NOT NULL PRIMARY KEY,
  `user_id` BIGINT NULL,
  `role_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_user_to_role_user_id` (`user_id`),
  KEY `ix_user_to_role_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user_to_wings` (
  `usertowing_id` BIGINT NOT NULL PRIMARY KEY,
  `user_id` BIGINT NULL,
  `wing_id` BIGINT NULL,
  `created_at` VARCHAR(255) NULL,
  `updated_at` VARCHAR(255) NULL,
  KEY `ix_user_to_wings_user_id` (`user_id`),
  KEY `ix_user_to_wings_wing_id` (`wing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
