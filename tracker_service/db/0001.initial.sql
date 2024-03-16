-- Initial schema for task tracker service.
-- depends:


create schema if not exists tracker;

create table if not exists tracker.user (
    id        int  generated always as identity primary key,
    public_id text not null,
    name      text not null,
    email     text not null,
    role      text not null,
    constraint user_public_id_unique unique (public_id),
    constraint user_email_unique unique (email)
);

create table if not exists tracker.task (
    id          int  generated always as identity primary key,
    public_id   text not null,
    title       text not null,
    is_closed   text not null,
    assignee_id int not null references tracker.user (id),
    created_at  timestamp with time zone not null,
    updated_at  timestamp with time zone not null,
    constraint task_public_id_unique unique (public_id)
);
