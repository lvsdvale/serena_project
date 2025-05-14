-- 1. Tabelas independentes

CREATE TABLE "user" (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(32),
    create_time TIMESTAMP
);

CREATE TABLE caregiver (
    caregiver_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(user_id)
);

CREATE TABLE doctor (
    doctor_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(user_id),
    crm_number VARCHAR(45)
);

CREATE TABLE medication (
    medication_id SERIAL PRIMARY KEY,
    medication_name VARCHAR(100)
);

-- 2. Tabelas com dependência de user e caregiver

CREATE TABLE senior (
    senior_id SERIAL PRIMARY KEY,
    user_user_id INT REFERENCES "user"(user_id),
    caregiver_caregiver_id INT REFERENCES caregiver(caregiver_id),
    caregiver_user_id INT REFERENCES "user"(user_id),
    age INT
);

-- 3. Tabelas com dependência de senior

CREATE TABLE serena_device (
    serena_device_code VARCHAR(45) PRIMARY KEY,
    senior_senior_id INT REFERENCES senior(senior_id),
    senior_user_id INT REFERENCES "user"(user_id)
);

CREATE TABLE disease_diagnosis (
    disease_diagnosis_id SERIAL PRIMARY KEY,
    disease_name VARCHAR(90),
    senior_senior_id INT REFERENCES senior(senior_id),
    senior_user_user_id INT REFERENCES "user"(user_id),
    diagnosed_at VARCHAR(45)
);

CREATE TABLE complaint (
    complaint_id SERIAL PRIMARY KEY,
    symptom VARCHAR(100),
    serena_llm_response TEXT,
    create_time TIMESTAMP,
    senior_senior_id INT REFERENCES senior(senior_id),
    senior_user_user_id INT REFERENCES "user"(user_id)
);

-- 4. Prescrição e relacionamento com senior, doctor, user

CREATE TABLE prescription (
    prescription_id SERIAL PRIMARY KEY,
    doctor_doctor_id INT REFERENCES doctor(doctor_id),
    doctor_user_id INT REFERENCES "user"(user_id),
    senior_senior_id INT REFERENCES senior(senior_id),
    senior_user_id INT REFERENCES "user"(user_id),
    create_time TIMESTAMP,
    validation_time DATE
);

-- 5. prescription_item dependente da prescription

CREATE TABLE prescription_item (
    prescription_item_id SERIAL PRIMARY KEY,
    dosage VARCHAR(100),
    frequency_unit VARCHAR(20) CHECK (frequency_unit IN ('hour', 'day', 'week')),
    frequency_time INT,
    duration_unit VARCHAR(20) CHECK (duration_unit IN ('day', 'week', 'month')),
    duration_time INT,
    prescription_prescription_id INT REFERENCES prescription(prescription_id),
    description TEXT,
    medicine_name VARCHAR(45)
);

-- 6. Compartments dependente de serena_device

CREATE TABLE compartment (
    stock_id SERIAL PRIMARY KEY,
    medicine_name VARCHAR(80),
    amount INT,
    serena_device_serena_device_code VARCHAR(45) REFERENCES serena_device(serena_device_code)
);
