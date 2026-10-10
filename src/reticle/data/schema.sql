-- Reticle schema, migration 1: the vehicle catalog.
-- Hierarchy: manufacturer -> model -> generation -> trim.
-- Revlo's rarity tier lives on the trim; the project's own rarity score is separate.

CREATE TABLE manufacturers (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE COLLATE NOCASE,
    country TEXT
);

CREATE TABLE models (
    id              INTEGER PRIMARY KEY,
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(id),
    name            TEXT NOT NULL COLLATE NOCASE,
    body_style      TEXT,
    UNIQUE (manufacturer_id, name)
);

CREATE TABLE generations (
    id         INTEGER PRIMARY KEY,
    model_id   INTEGER NOT NULL REFERENCES models(id),
    code       TEXT NOT NULL COLLATE NOCASE,
    year_start INTEGER,
    year_end   INTEGER,
    notes      TEXT,
    UNIQUE (model_id, code),
    CHECK (year_start IS NULL OR year_end IS NULL OR year_end >= year_start)
);

CREATE TABLE revlo_tiers (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL UNIQUE,
    xp         INTEGER NOT NULL
);

INSERT INTO revlo_tiers (name, sort_order, xp) VALUES
    ('Common',    1,   50),
    ('Uncommon',  2,  120),
    ('Rare',      3,  300),
    ('Elite',     4,  500),
    ('Exotic',    5,  700),
    ('Legendary', 6, 1500),
    ('Mythic',    7, 3000);

CREATE TABLE trims (
    id                   INTEGER PRIMARY KEY,
    generation_id        INTEGER NOT NULL REFERENCES generations(id),
    name                 TEXT NOT NULL COLLATE NOCASE,
    revlo_tier_id        INTEGER REFERENCES revlo_tiers(id),
    project_rarity_score REAL CHECK (project_rarity_score IS NULL
                                     OR project_rarity_score BETWEEN 0 AND 10),
    engine               TEXT,
    displacement_l       REAL,
    cylinders            INTEGER,
    aspiration           TEXT,
    horsepower_hp        INTEGER,
    torque_nm            INTEGER,
    transmission         TEXT,
    drivetrain           TEXT,
    curb_weight_kg       INTEGER,
    length_mm            INTEGER,
    width_mm             INTEGER,
    height_mm            INTEGER,
    fuel_type            TEXT,
    fuel_economy_l_100km REAL,
    msrp_cad             INTEGER,
    doors                INTEGER,
    seats                INTEGER,
    cargo_l              INTEGER,
    UNIQUE (generation_id, name)
);

CREATE TABLE vehicle_aliases (
    id            INTEGER PRIMARY KEY,
    alias         TEXT NOT NULL COLLATE NOCASE,
    model_id      INTEGER REFERENCES models(id),
    generation_id INTEGER REFERENCES generations(id),
    trim_id       INTEGER REFERENCES trims(id),
    CHECK ((model_id IS NOT NULL) + (generation_id IS NOT NULL)
           + (trim_id IS NOT NULL) = 1)
);

CREATE INDEX idx_models_manufacturer ON models(manufacturer_id);
CREATE INDEX idx_generations_model   ON generations(model_id);
CREATE INDEX idx_trims_generation    ON trims(generation_id);
CREATE INDEX idx_aliases_alias       ON vehicle_aliases(alias);