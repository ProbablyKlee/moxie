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
CREATE TABLE IF NOT EXISTS action
(
    user_id BIGINT NOT NULL,
    target_id BIGINT NOT NULL,
    action_type VARCHAR(255) NOT NULL,
    action_count BIGINT NOT NULL,
    CONSTRAINT action_pk PRIMARY KEY (user_id, target_id, action_type),
    CONSTRAINT action_user_fk FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT action_target_fk FOREIGN KEY (target_id)
        REFERENCES users (user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS action_user_id_idx ON action (user_id);
CREATE INDEX IF NOT EXISTS action_target_id_idx ON action (target_id);

CREATE OR REPLACE FUNCTION insert_action_item(p_user_id BIGINT, p_target_id BIGINT, p_action_type VARCHAR(255))
RETURNS VOID AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM action
        WHERE user_id = p_user_id
            AND target_id = p_target_id
            AND action_type = p_action_type
    ) THEN
        UPDATE action
        SET action_count = action_count + 1
        WHERE user_id = p_user_id
            AND target_id = p_target_id
            AND action_type = p_action_type;
    ELSE
        INSERT INTO action (user_id, target_id, action_type, action_count)
        VALUES (p_user_id, p_target_id, p_action_type, 1);
    END IF;
END;
$$ LANGUAGE plpgsql;
