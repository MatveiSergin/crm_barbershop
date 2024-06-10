create schema if not exists main;

create table main.Client (
    id serial PRIMARY KEY,
    name varchar not null,
    surname varchar not null,
    phone bigint unique not null,
    mail varchar unique
);

create table main.Barbershop (
    id serial PRIMARY KEY,
    region varchar,
    city varchar,
    street varchar,
    house varchar,
    postal_code int unique,
    phone bigint unique,
    mail varchar unique not null
);

create table main.Service (
    id serial PRIMARY KEY,
    price int check (price > 0),
    name varchar not null unique,
    description varchar
);

create table main.Position (
	id serial PRIMARY KEY,
	position varchar unique not null,
    has_accept_appointments bool DEFAULT true
);

create table main.Staff (
    id serial primary key,
    barbershop_id int REFERENCES main.Barbershop(id) on delete set null,
    name varchar not null,
    surname varchar not null,
    patronymic varchar,
    position_id int references main.Position(id) not null,
    phone bigint unique not null,
    mail varchar unique not null
);

create table main.Documents (
    staff_id int PRIMARY KEY references main.staff(id) on delete CASCADE,
    passport bigint not null unique,
    employment_record_number bigint not null unique,
    snils bigint not null unique
);

create table main.Appointment (
    id serial PRIMARY KEY,
    staff_id int references main.staff(id) on delete set null,
    client_id int references main.client(id) on delete set null,
    service_id int references main.service(id) on delete set null,
    status_code int DEFAULT 0,
    data timestamp without time zone
);

create table main.Master_service (
    id serial PRIMARY KEY,
    staff_id int references main.staff(id) on delete cascade,
    service_id int references main.service(id) on delete cascade
);