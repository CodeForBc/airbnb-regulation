CREATE TABLE IF NOT EXISTS listing (
    airbnb_listing_id VARCHAR(20) PRIMARY KEY,
    baths INT,
    beds INT,
    latitude DECIMAL(8,6), 
    location VARCHAR(20),
    longitude DECIMAL(9,6),
    name VARCHAR(100),
    person_capacity INT,
    registration_number VARCHAR(20),
    room_type VARCHAR(20),
    title VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS policy (
    policy_id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255),
    policy_description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS listing_policy_result (
    result_id SERIAL PRIMARY KEY,
    airbnb_listing_id VARCHAR(50),
    policy_id INT,
    policy_result BOOLEAN,
    result_details VARCHAR(255),
    result_datetime TIMESTAMP,
    FOREIGN KEY (airbnb_listing_id) REFERENCES listing(airbnb_listing_id),
    FOREIGN KEY (policy_id) REFERENCES policy(policy_id)
);

INSERT INTO listing (airbnb_listing_id, baths, beds, latitude, location, longitude, name, person_capacity, registration_number, room_type, title) VALUES
('1', 1, 1, 49.2827, 'Vancouver', 123.1207, 'Listing 1', 2, '12345', 'Private Room', 'Beautiful Room in Vancouver'),
('2', 2, 2, 49.2827, 'Vancouver', 123.1207, 'Listing 2', 4, '67890', 'Entire Home', 'Luxury Home in Vancouver'),
('3', 1, 1, 49.2827, 'Vancouver', 123.1207, 'Listing 3', 2, '11223', 'Shared Room', 'Cozy Room in Vancouver');

INSERT INTO policy (policy_id, policy_name, policy_description) VALUES
(1, 'Policy 1', 'This is policy 1'),
(2, 'Policy 2', 'This is policy 2'),
(3, 'Policy 3', 'This is policy 3');

INSERT INTO listing_policy_result (result_id, airbnb_listing_id, policy_id, policy_result, result_details, result_datetime) VALUES
(1, '1', 1, TRUE, 'Passed policy 1', CURRENT_TIMESTAMP),
(2, '2', 2, FALSE, 'Failed policy 2', CURRENT_TIMESTAMP),
(3, '3', 3, TRUE, 'Passed policy 3', CURRENT_TIMESTAMP);