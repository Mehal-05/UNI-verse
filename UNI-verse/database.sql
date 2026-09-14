CREATE DATABASE IF NOT EXISTS universe_db;

USE universe_db;

CREATE TABLE campus (
    campus_id INT PRIMARY KEY AUTO_INCREMENT,
    campus_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE department (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL,
    campus_id INT NOT NULL,
    FOREIGN KEY (campus_id) REFERENCES campus(campus_id)
);

CREATE TABLE student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    campus_id INT NOT NULL,
    department_id INT NOT NULL,
    cgpa DECIMAL(3,2) NOT NULL,
    backlogs INT DEFAULT 0,
    graduation_year INT NOT NULL,
    FOREIGN KEY (campus_id) REFERENCES campus(campus_id),
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

CREATE TABLE company (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(100)
);

CREATE TABLE placement_drive (
    drive_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    campus_id INT NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    package_lpa DECIMAL(5,2) NOT NULL,
    minimum_cgpa DECIMAL(3,2) NOT NULL,
    maximum_backlogs INT DEFAULT 0,
    drive_date DATE,
    FOREIGN KEY (company_id) REFERENCES company(company_id),
    FOREIGN KEY (campus_id) REFERENCES campus(campus_id)
);

CREATE TABLE application (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    drive_id INT NOT NULL,
    status VARCHAR(30) DEFAULT 'Applied',
    applied_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (drive_id) REFERENCES placement_drive(drive_id)
);

CREATE TABLE placement (
    placement_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    company_id INT NOT NULL,
    package_lpa DECIMAL(5,2) NOT NULL,
    placement_year INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (company_id) REFERENCES company(company_id)
);