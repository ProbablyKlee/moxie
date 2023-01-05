--
-- The MIT License (MIT)
-- Copyright (c) 2022-Present Lia Marie
-- Permission is hereby granted, free of charge, to any person obtaining a
-- copy of this software and associated documentation files (the "Software"),
-- to deal in the Software without restriction, including without limitation
-- the rights to use, copy, modify, merge, publish, distribute, sublicense,
-- and/or sell copies of the Software, and to permit persons to whom the
-- Software is furnished to do so, subject to the following conditions:
-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
-- OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
-- FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
-- DEALINGS IN THE SOFTWARE.
--
CREATE TABLE IF NOT EXISTS prefix (
    prefix_id bigserial NOT NULL,
    guild_id bigint NOT NULL,
    prefix text NOT NULL,
    CONSTRAINT prefix_pk PRIMARY KEY (prefix_id),
    CONSTRAINT prefix_guild_fk FOREIGN KEY (guild_id) REFERENCES guild (guild_id)
);

CREATE INDEX IF NOT EXISTS prefix_prefix_id_idx ON prefix (prefix_id);
CREATE INDEX IF NOT EXISTS prefix_guild_id_idx ON prefix (guild_id);

CREATE OR REPLACE FUNCTION insert_default_prefix()
RETURNS TRIGGER AS
$BODY$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM prefix WHERE guild_id = NEW.guild_id) THEN
        INSERT INTO prefix (guild_id, prefix) VALUES (NEW.guild_id, 'fishie');
    END IF;
    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS insert_default_prefix_trigger ON guild;
CREATE TRIGGER insert_default_prefix_trigger
AFTER INSERT ON guild
FOR EACH ROW EXECUTE PROCEDURE insert_default_prefix();
