-- Initial schema for billing service.
-- depends:


create schema if not exists billing;

create table if not exists billing.user (
    id        int  generated always as identity primary key,
    public_id text not null,
    name      text not null,
    email     text not null,
    role      text not null,
    constraint user_public_id_unique unique (public_id),
    constraint user_email_unique unique (email)
);

create table if not exists billing.task (
    id          int  generated always as identity primary key,
    public_id   text not null,
    assignee_price int not null,
    complete_price int not null,
    constraint task_public_id_unique unique (public_id)
);

create table if not exists billing.balance (
    id      int  generated always as identity primary key,
    user_id int  not null references billing.user (id),
    money   int  not null,
    constraint balance_user_id_unique unique (user_id)
);

create table if not exists billing.payment_journal (
    id       int  generated always as identity primary key,
    user_id  int  not null,
    amount   int  not null, 
    op       text not null  -- credit / debit.
);