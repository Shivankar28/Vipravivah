CREATE TABLE profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    looking_for VARCHAR(50),
    age_min INT,
    age_max INT,
    mother_tongue VARCHAR(50),
    gotra VARCHAR(50)
);

CREATE TABLE profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    looking_for VARCHAR(50),
    gender VARCHAR(10),
    name_first VARCHAR(50),
    name_middle VARCHAR(50),
    name_last VARCHAR(50),
    dob DATE,
    religion VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(15)
);


CREATE TABLE profile2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temp_address VARCHAR(255),
    temp_city VARCHAR(50),
    temp_district VARCHAR(50),
    temp_state VARCHAR(50),
    temp_pincode VARCHAR(10),
    perm_address VARCHAR(255),
    perm_city VARCHAR(50),
    perm_district VARCHAR(50),
    perm_state VARCHAR(50),
    perm_pincode VARCHAR(10),
    lives_with_family VARCHAR(10),
    marital_status VARCHAR(20),
    diet VARCHAR(255)
);

CREATE TABLE profile3 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    qualification VARCHAR(50),
    specialization VARCHAR(50),
    working_status VARCHAR(20),
    works_with VARCHAR(50),
    job_title VARCHAR(50),
    income VARCHAR(255),
    instagram VARCHAR(255), -- Column for Instagram profile link
    facebook VARCHAR(255),  -- Column for Facebook profile link
    linkedin VARCHAR(255)   -- Column for LinkedIn profile link
);


CREATE TABLE profile4 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identity_type ENUM('adhar_card', 'passport', 'pan_card') NOT NULL,
    identity_number VARCHAR(20) NOT NULL
);



CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
