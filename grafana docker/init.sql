CREATE TABLE test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100),
    price DECIMAL(5, 2)
);

INSERT INTO
    test_table (name, location, price)
VALUES
    ('Cozy Cottage', 'New York', 150.00),
    ('Urban Loft', 'Los Angeles', 210.00),
    ('Country Retreat', 'Nashville', 85.00);