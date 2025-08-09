-- Table: public.custom_data

-- DROP TABLE IF EXISTS public.custom_data;

CREATE TABLE IF NOT EXISTS public.custom_data
(
    case_id text COLLATE pg_catalog."default" NOT NULL,
    family_progress_status text COLLATE pg_catalog."default",
    CONSTRAINT custom_data_pkey PRIMARY KEY (case_id)
)

TABLESPACE pg_default;