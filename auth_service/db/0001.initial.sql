-- Tables for storing auth info.
--

create schema if not exists auth;

create table if not exists auth.user (
    id        int  generated always as identity primary key,
    public_id text not null,
    beak_form text not null,
    name      text not null,
    email     text not null,
    role      text not null,
    constraint user_public_id_unique unique (public_id),
    constraint user_beak_form_unique unique (beak_form),
    constraint user_email_unique unique (email)
);
