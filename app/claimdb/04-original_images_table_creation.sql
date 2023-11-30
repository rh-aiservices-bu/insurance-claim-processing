-- Table: claims.original_images

-- DROP TABLE and SEQUENCE (with CASCADE)

-- DROP TABLE IF EXISTS claims.original_images CASCADE;

-- SEQUENCE: claims.original_images_id_seq

CREATE SEQUENCE IF NOT EXISTS claims.original_images_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

-- Table: claims.original_images

CREATE TABLE IF NOT EXISTS claims.original_images
(
    id integer NOT NULL DEFAULT nextval('claims.original_images_id_seq'::regclass),
    image_name text COLLATE pg_catalog."default" NOT NULL,
    image_key text COLLATE pg_catalog."default" NOT NULL,
    claim_id integer NOT NULL,
    CONSTRAINT original_images_pkey PRIMARY KEY (id),
    CONSTRAINT fk_claim_id FOREIGN KEY (claim_id)
        REFERENCES claims.claims (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

-- Link Table to Sequence    

ALTER SEQUENCE claims.original_images_id_seq 
    OWNED BY claims.original_images.id;