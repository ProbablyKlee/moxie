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
CREATE TABLE IF NOT EXISTS users
(
    user_id bigint NOT NULL,
    emoji_server_id bigint NOT NULL DEFAULT 0,  -- 0 = no emoji server
    time_zone varchar(255) NOT NULL DEFAULT 'UTC',
    added_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT user_pk PRIMARY KEY (user_id)
);

CREATE INDEX IF NOT EXISTS user_user_id_idx ON users (user_id);
