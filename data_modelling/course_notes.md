# Data Modelling

## Class Overview (1:50 hours)

**Learning Objectives:**
- Understand the difference between OLTP and OLAP systems
- Identify and design Facts and Dimensions
- Apply different dimensional modeling techniques (SCD Types 0, 1, 2)
- Compare Star Schema vs Snowflake Schema
- Understand normalization vs denormalization trade-offs
- Practice designing a dimensional model for a real-world scenario (Hospital)

**Class Structure:**
1. Introduction & Concepts (30 min)
2. Dimensional Modeling Techniques (25 min)
3. Schema Design Patterns (20 min)
4. Workshop: Hospital Data Model (35 min)

---

## 1. Introduction: OLTP vs OLAP (10 minutes)

### OLTP (Online Transaction Processing)
**Purpose:** Day-to-day operations
**Characteristics:**
- High volume of short transactions (INSERT, UPDATE, DELETE)
- Normalized data structures
- Focus on data integrity and consistency
- Example: E-commerce checkout system, banking transactions

### OLAP (Online Analytical Processing)
**Purpose:** Business intelligence and analytics
**Characteristics:**
- Complex queries with aggregations
- Denormalized data structures (optimized for reading)
- Focus on query performance
- Example: Sales reports, trend analysis, KPI dashboards

### Key Vocabulary (CLIL)
- **Transaction:** A single business event (e.g., purchase, payment)
- **Aggregation:** Combining data (SUM, COUNT, AVG)
- **Normalized:** Data organized to reduce redundancy
- **Denormalized:** Data duplicated for faster queries

---

## 2. Facts and Dimensions (20 minutes)

### Facts
**Definition:** Quantitative, measurable data about business events

**Characteristics:**
- Numeric values (measures)
- Can be aggregated (SUM, AVG, COUNT, MIN, MAX)
- Represent business processes
- Usually large tables (millions of rows)

**Types of Facts:**
1. **Additive:** Can be summed across all dimensions (e.g., sales_amount, quantity)
2. **Semi-additive:** Can be summed across some dimensions (e.g., account_balance - can't sum across time)
3. **Non-additive:** Cannot be summed (e.g., unit_price, ratios)

**Example - Sales Fact Table:**
```sql
fact_sales (
    sale_id           -- Surrogate key
    date_key          -- Foreign key to dim_date
    product_key       -- Foreign key to dim_product
    customer_key      -- Foreign key to dim_customer
    store_key         -- Foreign key to dim_store
    quantity          -- Measure (additive)
    unit_price        -- Measure (non-additive)
    discount_amount   -- Measure (additive)
    total_amount      -- Measure (additive)
)
```

### Dimensions
**Definition:** Descriptive attributes that provide context to facts

**Characteristics:**
- Textual/categorical data
- Used for filtering, grouping, and labeling
- Relatively small tables (thousands of rows)
- Contain hierarchies

**Common Dimensions:**
- **Time/Date:** day, month, quarter, year, is_weekend
- **Product:** product_name, category, brand, supplier
- **Customer:** name, age_group, location, segment
- **Location:** address, city, region, country

**Example - Product Dimension:**
```sql
dim_product (
    product_key       -- Surrogate key (auto-increment)
    product_id        -- Natural key (from source system)
    product_name
    category
    subcategory
    brand
    supplier
    unit_cost
    launch_date
    is_active
    -- SCD tracking fields (we'll see these later)
    effective_date
    expiration_date
    is_current
)
```

### Hierarchies in Dimensions
Dimensions often have natural hierarchies for drill-down analysis:

**Time Hierarchy:**
```
Year → Quarter → Month → Week → Day
2024 → Q4      → Nov   → W48  → Nov 30
```

**Product Hierarchy:**
```
Department → Category → Subcategory → Product
Electronics → Audio    → Headphones  → Sony WH-1000XM5
```

**Geographic Hierarchy:**
```
Country → Region → City → Store
Spain   → Aragon → Zaragoza → Store #042
```

---

## 3. Slowly Changing Dimensions (SCD) (25 minutes)

Dimensions change over time. How do we handle these changes?

### Type 0: No Changes Allowed
**Strategy:** Never update; original values are kept forever

**Use Case:** Historical facts that should never change (e.g., birth_date, social_security_number)

**Example:**
```sql
dim_customer (
    customer_key,
    customer_id,
    birth_date,      -- Never changes
    birth_country    -- Never changes
)
```

### Type 1: Overwrite
**Strategy:** Update the record, no history kept

**Pros:** 
- Simple implementation
- Saves storage space
- Always shows current information

**Cons:** 
- Loses historical accuracy
- Cannot analyze trends over time

**Use Case:** Correcting errors, attributes that don't require history (e.g., fixing a misspelled name, updating an email address)

**Example:**
```sql
-- Before: Customer moves
customer_key | customer_id | name        | city      | phone
1001         | C123        | John Smith  | Madrid    | 611-111-111

-- After: UPDATE (overwrites)
customer_key | customer_id | name        | city      | phone
1001         | C123        | John Smith  | Barcelona | 622-222-222
```

**SQL Implementation:**
```sql
UPDATE dim_customer
SET city = 'Barcelona',
    phone = '622-222-222',
    last_updated = CURRENT_TIMESTAMP
WHERE customer_id = 'C123';
```

### Type 2: Add New Row (Most Common)
**Strategy:** Create a new record for each change, keeping full history

**Fields Added:**
- `effective_date` / `start_date`: When this version became active
- `expiration_date` / `end_date`: When this version expired (NULL or 9999-12-31 for current)
- `is_current`: Flag indicating the current version (TRUE/FALSE or 1/0)
- `version`: Optional version number

**Pros:**
- Complete historical accuracy
- Can analyze changes over time
- Audit trail

**Cons:**
- Increased storage
- More complex queries
- Dimension table grows larger

**Use Case:** Price changes, customer address changes, product category changes

**Example:**
```sql
-- Version 1: Customer in Madrid (Jan-Jun 2024)
customer_key | customer_id | name       | city    | effective_date | expiration_date | is_current
1001         | C123        | John Smith | Madrid  | 2024-01-01     | 2024-06-30      | 0

-- Version 2: Customer moves to Barcelona (Jul 2024 - present)
customer_key | customer_id | name       | city      | effective_date | expiration_date | is_current
1002         | C123        | John Smith | Barcelona | 2024-07-01     | 9999-12-31      | 1
```

**SQL Implementation:**
```sql
-- Step 1: Close the current record
UPDATE dim_customer
SET expiration_date = '2024-06-30',
    is_current = 0
WHERE customer_id = 'C123' AND is_current = 1;

-- Step 2: Insert new record
INSERT INTO dim_customer (customer_id, name, city, effective_date, expiration_date, is_current)
VALUES ('C123', 'John Smith', 'Barcelona', '2024-07-01', '9999-12-31', 1);
```

**Querying with SCD Type 2:**
```sql
-- Get current customer information
SELECT * FROM dim_customer
WHERE customer_id = 'C123' AND is_current = 1;

-- Get customer information as of a specific date
SELECT * FROM dim_customer
WHERE customer_id = 'C123'
  AND '2024-05-15' BETWEEN effective_date AND expiration_date;

-- Analyze sales by customer's city over time (historical accuracy)
SELECT 
    d.city,
    YEAR(f.sale_date) as year,
    SUM(f.total_amount) as total_sales
FROM fact_sales f
JOIN dim_customer d ON f.customer_key = d.customer_key
WHERE d.customer_id = 'C123'
GROUP BY d.city, YEAR(f.sale_date);
```

### Type 3: Add New Column
**Strategy:** Add columns to store both old and new values (limited history)

**Use Case:** When you need to compare only the previous and current value

**Example:**
```sql
customer_key | customer_id | name       | current_city | previous_city
1001         | C123        | John Smith | Barcelona    | Madrid
```

**Pros:**
- Easy to compare current vs previous
- No new rows added

**Cons:**
- Limited to only one previous value
- Not suitable for long-term historical analysis

### Type 6 (Hybrid: 1+2+3)
**Strategy:** Combines Type 1, 2, and 3 techniques

**Structure:**
- Keep history like Type 2
- Overwrite current attributes in all rows (Type 1)
- Keep previous value (Type 3)

**Example:**
```sql
customer_key | customer_id | historical_city | current_city | previous_city | effective_date | is_current
1001         | C123        | Madrid          | Barcelona    | Madrid        | 2024-01-01     | 0
1002         | C123        | Barcelona       | Barcelona    | Madrid        | 2024-07-01     | 1
```

---

## 4. Schema Design Patterns (20 minutes)

### Star Schema ⭐
**Definition:** Facts at the center, dimensions directly connected (denormalized)

**Characteristics:**
- Simple structure
- Fast query performance
- Denormalized dimensions
- Easy for business users to understand

**Example - E-commerce Star Schema:**
```
            dim_date
                |
                |
dim_customer ------- fact_sales ------- dim_product
                |
                |
            dim_store
```

**SQL Example:**
```sql
-- Create Star Schema
CREATE TABLE fact_sales (
    sale_id BIGINT PRIMARY KEY,
    date_key INT,
    customer_key INT,
    product_key INT,
    store_key INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_store(store_key)
);

CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    product_id VARCHAR(50),
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    supplier_name VARCHAR(200),  -- Denormalized!
    supplier_country VARCHAR(100) -- Denormalized!
);
```

**Query Example:**
```sql
-- Simple 2-table joins (fast!)
SELECT 
    p.category,
    p.brand,
    SUM(f.total_amount) as total_sales,
    SUM(f.quantity) as units_sold
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
WHERE p.category = 'Electronics'
GROUP BY p.category, p.brand
ORDER BY total_sales DESC;
```

**Pros:**
- Fewer joins = faster queries
- Simple for BI tools
- Optimized for read performance

**Cons:**
- Data redundancy
- More storage needed
- Updates require changing multiple rows

### Snowflake Schema ❄️
**Definition:** Normalized dimensions with sub-dimensions (hierarchies separated)

**Characteristics:**
- Normalized structure
- Multiple levels of dimensions
- Less data redundancy
- More complex queries (more joins)

**Example - E-commerce Snowflake Schema:**
```
                    dim_date
                        |
                        |
    dim_customer ------- fact_sales ------- dim_product ------- dim_category
         |                   |                   |
         |                   |                   |
    dim_customer_segment  dim_store        dim_brand
                              |
                              |
                          dim_region
```

**SQL Example:**
```sql
-- Normalized structure
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    product_id VARCHAR(50),
    product_name VARCHAR(200),
    brand_key INT,  -- Foreign key to dim_brand
    category_key INT,  -- Foreign key to dim_category
    FOREIGN KEY (brand_key) REFERENCES dim_brand(brand_key),
    FOREIGN KEY (category_key) REFERENCES dim_category(category_key)
);

CREATE TABLE dim_brand (
    brand_key INT PRIMARY KEY,
    brand_name VARCHAR(100),
    country VARCHAR(100)
);

CREATE TABLE dim_category (
    category_key INT PRIMARY KEY,
    category_name VARCHAR(100),
    department VARCHAR(100)
);

CREATE TABLE dim_store (
    store_key INT PRIMARY KEY,
    store_id VARCHAR(50),
    store_name VARCHAR(200),
    region_key INT,
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key)
);

CREATE TABLE dim_region (
    region_key INT PRIMARY KEY,
    city VARCHAR(100),
    province VARCHAR(100),
    country VARCHAR(100)
);
```

**Query Example:**
```sql
-- More joins required (slower)
SELECT 
    c.category_name,
    b.brand_name,
    r.country as store_country,
    SUM(f.total_amount) as total_sales
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_category c ON p.category_key = c.category_key  -- Extra join
JOIN dim_brand b ON p.brand_key = b.brand_key            -- Extra join
JOIN dim_store s ON f.store_key = s.store_key
JOIN dim_region r ON s.region_key = r.region_key         -- Extra join
GROUP BY c.category_name, b.brand_name, r.country;
```

**Pros:**
- Less storage (no redundancy)
- Easier to maintain consistency
- Cleaner data model

**Cons:**
- More joins = slower queries
- More complex for business users
- BI tools may struggle

### Star vs Snowflake Comparison

| Aspect | Star Schema ⭐ | Snowflake Schema ❄️ |
|--------|--------------|-------------------|
| **Structure** | Denormalized | Normalized |
| **Number of Joins** | Fewer (2-3) | More (4-6+) |
| **Query Performance** | Faster | Slower |
| **Storage** | More space needed | Less space |
| **Maintenance** | More complex updates | Easier updates |
| **Data Redundancy** | High | Low |
| **Business User Friendliness** | Easy to understand | More complex |
| **Best For** | OLAP, BI, Dashboards | When storage is critical |

### When to Use Each?

**Choose Star Schema when:**
- Query performance is the priority
- Storage is not a concern
- Business users need simple queries
- Building data warehouses for analytics
- Using BI tools (Power BI, Tableau)

**Choose Snowflake Schema when:**
- Storage optimization is critical
- Data consistency is more important than speed
- You have deep hierarchies
- Database is frequently updated

**Real-World Practice:**
Most modern data warehouses use **Star Schema** because:
- Storage is cheap
- Query speed matters more
- Simplicity for analysts is valuable
- BI tools work better with it

---

## 5. Normalization vs Denormalization (15 minutes)

### Normalization
**Definition:** Organizing data to reduce redundancy and dependency

**Normal Forms (Brief Overview):**

**1NF (First Normal Form):**
- Atomic values (no arrays or lists in a cell)
- Each column has a unique name
- Order doesn't matter

**2NF (Second Normal Form):**
- Must be in 1NF
- No partial dependencies (all non-key columns depend on the entire primary key)

**3NF (Third Normal Form):**
- Must be in 2NF
- No transitive dependencies (non-key columns depend only on the primary key)

### Example: E-commerce Orders

**Unnormalized (Bad):**
```sql
orders (
    order_id,
    customer_name,
    customer_email,
    customer_city,
    customer_country,
    products,  -- "Laptop, Mouse, Keyboard" (violates 1NF!)
    total_amount
)
```

**Normalized (OLTP - Good for transactions):**
```sql
customers (
    customer_id PRIMARY KEY,
    customer_name,
    customer_email,
    customer_city,
    customer_country
)

orders (
    order_id PRIMARY KEY,
    customer_id FOREIGN KEY,
    order_date,
    total_amount
)

order_items (
    order_item_id PRIMARY KEY,
    order_id FOREIGN KEY,
    product_id FOREIGN KEY,
    quantity,
    unit_price
)

products (
    product_id PRIMARY KEY,
    product_name,
    category,
    brand
)
```

**Denormalized (OLAP - Good for analytics):**
```sql
fact_order_items (
    order_item_id,
    order_id,
    order_date,
    customer_id,
    customer_name,        -- Duplicated!
    customer_city,        -- Duplicated!
    customer_country,     -- Duplicated!
    product_id,
    product_name,         -- Duplicated!
    category,             -- Duplicated!
    brand,                -- Duplicated!
    quantity,
    unit_price,
    total_amount
)
```

### Trade-offs

**Normalized (3NF):**
✅ No data redundancy
✅ Data consistency
✅ Easy to update
✅ Smaller storage
❌ Slow queries (many joins)
❌ Complex for reporting
**Use for:** OLTP systems, transactional databases

**Denormalized:**
✅ Fast queries (no joins)
✅ Simple reporting
✅ Optimized for reading
❌ Data redundancy
❌ More storage needed
❌ Complex updates
**Use for:** OLAP systems, data warehouses, reporting databases

---

## 6. Workshop: Hospital Data Model (35 minutes)

### Scenario
You are designing a data warehouse for a hospital network to analyze:
- Patient admissions and readmissions
- Doctor performance and workload
- Treatment costs and outcomes
- Department efficiency
- Medical equipment usage

### Business Questions to Answer:
1. What is the average length of stay by department and diagnosis?
2. Which doctors have the highest patient satisfaction scores?
3. What are the monthly admission trends by department?
4. What is the cost per treatment by diagnosis and insurance type?
5. Which departments have the highest readmission rates?
6. How many surgeries were performed by specialty and month?

### Activity (25 minutes)

**Step 1: Identify Facts (5 minutes)**
Work in pairs/groups. Identify the fact tables needed.
- What business processes do we measure?
- What are the metrics (measures)?

<details>
<summary>Hint: Think about events</summary>

Possible facts:
- Admissions/Visits
- Treatments/Procedures
- Prescriptions
- Lab Tests
- Surgeries
</details>

**Step 2: Identify Dimensions (5 minutes)**
What dimensions provide context?
- What do we filter by?
- What do we group by?

<details>
<summary>Hint: Common dimensions</summary>

Possible dimensions:
- Patient
- Doctor
- Department
- Date/Time
- Diagnosis
- Treatment/Procedure
- Insurance
- Room/Bed
</details>

**Step 3: Define SCD Types (5 minutes)**
For each dimension, decide:
- Which attributes change over time?
- Do we need historical tracking?
- What SCD type should we use?

**Step 4: Choose Schema (Star or Snowflake) (5 minutes)**
Decide on the schema design and justify your choice.

**Step 5: Draw the Model (5 minutes)**
Sketch the dimensional model with:
- Fact table(s) in the center
- Dimensions around them
- Key relationships

### Solution: Hospital Data Model

#### Fact Table: fact_patient_admission
```sql
CREATE TABLE fact_patient_admission (
    admission_id BIGINT PRIMARY KEY,
    
    -- Dimension Keys (Foreign Keys)
    patient_key INT,
    admitting_doctor_key INT,
    attending_doctor_key INT,
    department_key INT,
    admission_date_key INT,
    discharge_date_key INT,
    diagnosis_key INT,
    room_key INT,
    insurance_key INT,
    
    -- Measures (Metrics)
    length_of_stay_days INT,
    total_cost DECIMAL(10,2),
    medication_cost DECIMAL(10,2),
    procedure_cost DECIMAL(10,2),
    room_cost DECIMAL(10,2),
    patient_satisfaction_score INT,  -- 1-10
    is_readmission BOOLEAN,
    days_until_readmission INT,
    
    -- Degenerative Dimension (transaction identifier from source)
    admission_number VARCHAR(50),
    
    FOREIGN KEY (patient_key) REFERENCES dim_patient(patient_key),
    FOREIGN KEY (admitting_doctor_key) REFERENCES dim_doctor(doctor_key),
    FOREIGN KEY (attending_doctor_key) REFERENCES dim_doctor(doctor_key),
    FOREIGN KEY (department_key) REFERENCES dim_department(department_key),
    FOREIGN KEY (admission_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (discharge_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (diagnosis_key) REFERENCES dim_diagnosis(diagnosis_key),
    FOREIGN KEY (room_key) REFERENCES dim_room(room_key),
    FOREIGN KEY (insurance_key) REFERENCES dim_insurance(insurance_key)
);
```

#### Dimension: dim_patient (SCD Type 2)
```sql
CREATE TABLE dim_patient (
    patient_key INT PRIMARY KEY AUTO_INCREMENT,  -- Surrogate key
    patient_id VARCHAR(50),  -- Natural key (hospital ID)
    
    -- Attributes
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birth_date DATE,  -- Type 0 (never changes)
    gender VARCHAR(10),
    blood_type VARCHAR(5),  -- Type 0
    
    -- Address (Type 2 - track changes)
    address VARCHAR(200),
    city VARCHAR(100),
    province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    
    -- Contact (Type 1 - overwrite)
    phone VARCHAR(20),
    email VARCHAR(100),
    
    -- Insurance (Type 2 - track changes)
    primary_insurance_provider VARCHAR(100),
    
    -- SCD Type 2 tracking
    effective_date DATE,
    expiration_date DATE,
    is_current BOOLEAN,
    version INT
);
```

#### Dimension: dim_doctor (SCD Type 2)
```sql
CREATE TABLE dim_doctor (
    doctor_key INT PRIMARY KEY AUTO_INCREMENT,
    doctor_id VARCHAR(50),  -- Natural key
    
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    specialty VARCHAR(100),  -- Type 2 (can change)
    sub_specialty VARCHAR(100),
    department VARCHAR(100),  -- Type 2 (can transfer)
    license_number VARCHAR(50),  -- Type 0
    years_of_experience INT,  -- Type 1 (update yearly)
    education VARCHAR(500),  -- Type 1
    
    -- Contact
    email VARCHAR(100),
    phone VARCHAR(20),
    
    -- Status
    is_active BOOLEAN,
    hire_date DATE,
    
    -- SCD Type 2 tracking
    effective_date DATE,
    expiration_date DATE,
    is_current BOOLEAN
);
```

#### Dimension: dim_department
```sql
CREATE TABLE dim_department (
    department_key INT PRIMARY KEY AUTO_INCREMENT,
    department_id VARCHAR(50),
    department_name VARCHAR(100),
    department_type VARCHAR(50),  -- Emergency, Surgical, Medical, etc.
    floor_number INT,
    building VARCHAR(100),
    head_doctor_name VARCHAR(200),  -- Type 1
    phone_extension VARCHAR(20),
    budget_amount DECIMAL(15,2),
    is_active BOOLEAN
);
```

#### Dimension: dim_diagnosis (Slowly Changing)
```sql
CREATE TABLE dim_diagnosis (
    diagnosis_key INT PRIMARY KEY AUTO_INCREMENT,
    diagnosis_code VARCHAR(20),  -- ICD-10 code
    diagnosis_name VARCHAR(300),
    category VARCHAR(100),
    severity VARCHAR(50),  -- Mild, Moderate, Severe, Critical
    is_chronic BOOLEAN,
    average_treatment_days INT,
    requires_surgery BOOLEAN
);
```

#### Dimension: dim_date (Standard Date Dimension)
```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,  -- YYYYMMDD format (20241130)
    full_date DATE,
    day_of_week VARCHAR(10),
    day_of_month INT,
    day_of_year INT,
    week_of_year INT,
    month_number INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    holiday_name VARCHAR(100),
    fiscal_year INT,
    fiscal_quarter INT
);
```

#### Dimension: dim_insurance
```sql
CREATE TABLE dim_insurance (
    insurance_key INT PRIMARY KEY AUTO_INCREMENT,
    insurance_provider VARCHAR(100),
    plan_type VARCHAR(50),  -- Public, Private, Premium
    coverage_percentage DECIMAL(5,2),  -- 80.00 = 80%
    max_coverage_amount DECIMAL(15,2),
    copay_amount DECIMAL(10,2),
    deductible_amount DECIMAL(10,2),
    is_active BOOLEAN
);
```

#### Dimension: dim_room
```sql
CREATE TABLE dim_room (
    room_key INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(20),
    room_type VARCHAR(50),  -- ICU, Private, Semi-Private, Ward
    floor_number INT,
    building VARCHAR(100),
    department_key INT,
    bed_count INT,
    has_equipment BOOLEAN,
    daily_rate DECIMAL(10,2),
    is_available BOOLEAN,
    FOREIGN KEY (department_key) REFERENCES dim_department(department_key)
);
```

### Star Schema Diagram

```
                    dim_date (admission)
                            |
                            |
    dim_patient -----+      |      +------ dim_doctor (admitting)
                     |      |      |
                     |      |      |
    dim_insurance ---+--- fact_patient_admission ---+--- dim_doctor (attending)
                     |      |      |
                     |      |      |
    dim_diagnosis ---+      |      +------ dim_department
                            |
                            |
                    dim_room     dim_date (discharge)
```

### Example Analytical Queries

**1. Average length of stay by department and diagnosis:**
```sql
SELECT 
    dep.department_name,
    diag.diagnosis_name,
    AVG(f.length_of_stay_days) as avg_stay_days,
    COUNT(*) as total_admissions,
    AVG(f.total_cost) as avg_cost
FROM fact_patient_admission f
JOIN dim_department dep ON f.department_key = dep.department_key
JOIN dim_diagnosis diag ON f.diagnosis_key = diag.diagnosis_key
GROUP BY dep.department_name, diag.diagnosis_name
ORDER BY avg_stay_days DESC;
```

**2. Doctor performance and workload:**
```sql
SELECT 
    doc.first_name || ' ' || doc.last_name as doctor_name,
    doc.specialty,
    COUNT(*) as total_patients,
    AVG(f.patient_satisfaction_score) as avg_satisfaction,
    AVG(f.length_of_stay_days) as avg_stay,
    SUM(f.total_cost) as total_revenue
FROM fact_patient_admission f
JOIN dim_doctor doc ON f.attending_doctor_key = doc.doctor_key
WHERE doc.is_current = 1  -- Current version only
GROUP BY doctor_name, doc.specialty
HAVING COUNT(*) > 10  -- Doctors with more than 10 patients
ORDER BY avg_satisfaction DESC;
```

**3. Monthly admission trends:**
```sql
SELECT 
    d.year,
    d.month_name,
    dep.department_name,
    COUNT(*) as admissions,
    COUNT(CASE WHEN f.is_readmission THEN 1 END) as readmissions,
    ROUND(COUNT(CASE WHEN f.is_readmission THEN 1 END) * 100.0 / COUNT(*), 2) as readmission_rate
FROM fact_patient_admission f
JOIN dim_date d ON f.admission_date_key = d.date_key
JOIN dim_department dep ON f.department_key = dep.department_key
WHERE d.year = 2024
GROUP BY d.year, d.month_number, d.month_name, dep.department_name
ORDER BY d.month_number, admissions DESC;
```

**4. Cost analysis by diagnosis and insurance:**
```sql
SELECT 
    diag.diagnosis_name,
    ins.insurance_provider,
    ins.plan_type,
    COUNT(*) as patient_count,
    AVG(f.total_cost) as avg_total_cost,
    AVG(f.medication_cost) as avg_medication_cost,
    AVG(f.procedure_cost) as avg_procedure_cost,
    SUM(f.total_cost) as total_revenue
FROM fact_patient_admission f
JOIN dim_diagnosis diag ON f.diagnosis_key = diag.diagnosis_key
JOIN dim_insurance ins ON f.insurance_key = ins.insurance_key
GROUP BY diag.diagnosis_name, ins.insurance_provider, ins.plan_type
HAVING COUNT(*) > 5
ORDER BY total_revenue DESC;
```

**5. Readmission analysis:**
```sql
SELECT 
    dep.department_name,
    COUNT(*) as total_admissions,
    COUNT(CASE WHEN f.is_readmission THEN 1 END) as readmissions,
    ROUND(COUNT(CASE WHEN f.is_readmission THEN 1 END) * 100.0 / COUNT(*), 2) as readmission_rate,
    AVG(CASE WHEN f.is_readmission THEN f.days_until_readmission END) as avg_days_until_readmission
FROM fact_patient_admission f
JOIN dim_department dep ON f.department_key = dep.department_key
GROUP BY dep.department_name
ORDER BY readmission_rate DESC;
```

---

## Discussion Questions (10 minutes)

1. **Why did we choose Star Schema over Snowflake for the hospital model?**
   - Better query performance for analytics
   - Simpler for reporting tools
   - Hospital analysts need fast, simple queries

2. **Which dimensions need SCD Type 2 and why?**
   - `dim_patient`: Address and insurance changes (need history for accurate billing analysis)
   - `dim_doctor`: Department transfers, specialty changes (need history for performance tracking)

3. **What would happen if we used SCD Type 1 for patient addresses?**
   - We'd lose historical location data
   - Geographic analysis would be inaccurate
   - Can't track patient migration patterns

4. **Could we create additional fact tables? What other business processes could we track?**
   - `fact_lab_test`: Lab test results and costs
   - `fact_medication`: Prescriptions and pharmacy costs
   - `fact_surgery`: Surgical procedures and outcomes
   - `fact_appointment`: Outpatient visits
   - `fact_equipment_usage`: Medical equipment utilization

5. **Normalized vs Denormalized: When would you normalize the hospital model?**
   - If building the source OLTP system (patient management system)
   - If storage is extremely limited
   - If data consistency is more critical than query speed

---

## Key Takeaways

✅ **Facts** = Measures (numeric, aggregatable)
✅ **Dimensions** = Context (descriptive, categorical)
✅ **SCD Types** = How we handle dimension changes over time
   - Type 0: Never change
   - Type 1: Overwrite (no history)
   - Type 2: New row (full history) ⭐ Most common
✅ **Star Schema** = Denormalized, fast, simple (preferred for OLAP)
✅ **Snowflake Schema** = Normalized, slower, saves space
✅ **Normalization** = Good for OLTP (transactions)
✅ **Denormalization** = Good for OLAP (analytics)

---

## Additional Resources

- **Kimball Group**: The definitive guide to dimensional modeling
- **Tools**: ERDPlus, draw.io, Lucidchart for drawing schemas
- **Practice**: Model your own scenarios (e-commerce, university, bank)

## Homework (Optional)

Design a dimensional model for one of these scenarios:
1. **University**: Students, courses, enrollments, grades, professors
2. **E-commerce**: Products, customers, orders, payments, shipping
3. **Bank**: Accounts, transactions, customers, loans, credit cards

Include:
- At least 2 fact tables
- At least 5 dimensions
- SCD type decisions for each dimension
- Star schema diagram
- 3 analytical queries
