CREATE TABLE contracts (id integer unsigned primary key auto_increment, uri varchar(255), agency_name varchar(255), vendor_name varchar(255), reference_number varchar(255), contract_date date, description text, contract_period varchar(255), delivery_date date, contract_value decimal, comments text);
CREATE UNIQUE INDEX unique_contract ON contracts(agency_name, reference_number, contract_date);
