-- Table: claims.claims

-- DROP TABLE and SEQUENCE (with CASCADE)

-- DROP TABLE IF EXISTS claims.claims CASCADE;

-- SEQUENCE: claims.claims_id_seq

CREATE SEQUENCE IF NOT EXISTS claims.claims_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;


    OWNED BY claims.id;

-- Table: claims.claims

CREATE TABLE IF NOT EXISTS claims.claims
(
    id integer NOT NULL DEFAULT nextval('claims.claims_id_seq'::regclass),
    subject text COLLATE pg_catalog."default",
    body text COLLATE pg_catalog."default",
    summary text COLLATE pg_catalog."default",
    location text COLLATE pg_catalog."default",
    "time" text COLLATE pg_catalog."default",
    sentiment text COLLATE pg_catalog."default",
    CONSTRAINT claims_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

-- Link Table to Sequence    

ALTER SEQUENCE claims.claims_id_seq 
    OWNED BY claims.id;