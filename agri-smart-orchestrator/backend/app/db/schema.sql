CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    location_region TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    farm_name TEXT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    soil_type TEXT,
    total_area DECIMAL
);

CREATE TABLE crops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID REFERENCES farms(id),
    crop_name TEXT NOT NULL,
    variety TEXT,
    planting_date DATE,
    expected_harvest_date DATE,
    status TEXT
);

CREATE TABLE market_trends (
    id SERIAL PRIMARY KEY,
    crop_name TEXT NOT NULL,
    region TEXT NOT NULL,
    price_per_kg DECIMAL(10,2),
    demand_level TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE weather_records (
    id SERIAL PRIMARY KEY,
    farm_id UUID REFERENCES farms(id),
    forecast_type TEXT, 
    severity_level INTEGER,
    alert_message TEXT,
    valid_until TIMESTAMP
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assigned_to_agent TEXT,
    description TEXT,
    status TEXT DEFAULT 'Pending',
    priority INTEGER DEFAULT 2,
    due_date TIMESTAMP
);

CREATE TABLE agent_logs (
    id SERIAL PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    agent_name TEXT,
    action_taken TEXT,
    reasoning_process TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);