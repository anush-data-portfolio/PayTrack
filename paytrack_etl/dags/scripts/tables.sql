
-- Punches Table
CREATE TABLE punches (
    id SERIAL NOT NULL,
    punch_date DATE NOT NULL,
    punch_in TIME NOT NULL,
    punch_out TIME,
    pay_rate FLOAT NOT NULL,
    hours_worked INTERVAL GENERATED ALWAYS AS (punch_out - punch_in) STORED,
    PRIMARY KEY (id),
    CONSTRAINT punches_compound_key UNIQUE (punch_date, punch_in, punch_out)
);

-- Users Table
CREATE TABLE users (
    id SERIAL NOT NULL,
    first_name VARCHAR,
    username VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    PRIMARY KEY (id)
);

-- Departments Table
CREATE TABLE departments (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    PRIMARY KEY (id)
);

-- Employeedetails Table
CREATE TABLE employeedetails (
    id SERIAL NOT NULL,
    user_id INTEGER,
    department_id INTEGER,
    badge_number INTEGER NOT NULL,
    hire_date TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Timecards Table
CREATE TABLE timecards (
    id SERIAL NOT NULL,
    department_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (department_id) REFERENCES departments (id)
);

-- Timecard_Punches Table
CREATE TABLE timecard_punches (
    id SERIAL NOT NULL,
    timecard_id INTEGER,
    punch_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY (timecard_id) REFERENCES timecards (id),
    FOREIGN KEY (punch_id) REFERENCES punches (id)
);
