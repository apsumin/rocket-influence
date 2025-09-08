instagram_content

| column_name        | data_type                   |
| ------------------ | --------------------------- |
| id                 | uuid                        |
| client_internal_id | text                        |
| profile_url        | text                        |
| instagram_post_id  | text                        |
| shortcode          | text                        |
| video_url          | text                        |
| caption            | text                        |
| likes              | numeric                     |
| views              | numeric                     |
| video_duration     | double precision            |
| created_at         | timestamp without time zone |
| videoPlayCount     | numeric                     |
| commentsCounts     | numeric                     |
| is_summary         | text                        |


youtube

| column_name          | data_type                   |
| -------------------- | --------------------------- |
| internal_id          | integer                     |
| video_id             | text                        |
| url                  | text                        |
| title                | text                        |
| description          | text                        |
| text                 | text                        |
| hashtags             | ARRAY                       |
| published_at         | timestamp without time zone |
| duration             | interval                    |
| views                | integer                     |
| likes                | integer                     |
| comments_count       | integer                     |
| links_in_description | jsonb                       |
| channel_name         | text                        |
| channel_url          | text                        |
| channel_id           | text                        |
| channel_username     | text                        |
| channel_description  | text                        |
| channel_created_at   | date                        |
| channel_subscribers  | integer                     |
| channel_videos_count | integer                     |
| channel_total_views  | bigint                      |
| Transcrib            | text                        |



| column_name    | data_type                |
| -------------- | ------------------------ |
| id             | bigint                   |
| bloggerid      | bigint                   |
| channelid      | bigint                   |
| channelvideoid | bigint                   |
| description    | text                     |
| hashtags       | text                     |
| title          | text                     |
| url            | text                     |
| text           | text                     |
| is_vectorized  | boolean                  |
| created_at     | timestamp with time zone |
| changed_at     | timestamp with time zone |
