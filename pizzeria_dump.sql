BEGIN TRANSACTION;
CREATE TABLE client (
	id INTEGER NOT NULL, 
	full_name VARCHAR(150) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	email VARCHAR(100), 
	address VARCHAR(255), 
	PRIMARY KEY (id)
);
INSERT INTO "client" VALUES(1,'Иван Иванов','+79001112233','ivan@mail.ru','ул. Ленина, 1');
INSERT INTO "client" VALUES(2,'Мария Петрова','+79004445566',NULL,'ул. Пушкина, 10');
CREATE TABLE courier (
	id INTEGER NOT NULL, 
	employee_id INTEGER NOT NULL, 
	transport VARCHAR(50) NOT NULL, 
	delivery_zone VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (employee_id), 
	FOREIGN KEY(employee_id) REFERENCES employee (id)
);
INSERT INTO "courier" VALUES(1,3,'авто','Центральный');
CREATE TABLE dish (
	id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	dish_type VARCHAR(50) NOT NULL, 
	description VARCHAR(255), 
	price NUMERIC(10, 2) NOT NULL, 
	size VARCHAR(20), 
	is_available BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES menu_category (id)
);
INSERT INTO "dish" VALUES(1,1,'Маргарита','пицца','Томат, моцарелла, базилик',450,'30 см',1);
INSERT INTO "dish" VALUES(2,1,'Пепперони','пицца','Пепперони, моцарелла',550,'30 см',1);
INSERT INTO "dish" VALUES(3,2,'Кола','напиток','0.5 л',120,NULL,1);
CREATE TABLE employee (
	id INTEGER NOT NULL, 
	full_name VARCHAR(150) NOT NULL, 
	position VARCHAR(50) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	hire_date DATE NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "employee" VALUES(1,'Пётр Поваров','повар','+79007778899','2023-01-15');
INSERT INTO "employee" VALUES(2,'Ольга Официантова','официант','+79001231234','2023-05-01');
INSERT INTO "employee" VALUES(3,'Сергей Курьеров','курьер','+79005556677','2023-06-10');
CREATE TABLE ingredient (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	unit VARCHAR(20) NOT NULL, 
	stock_qty NUMERIC(12, 3) NOT NULL, 
	purchase_price NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO "ingredient" VALUES(1,'Моцарелла','г',5000,0.8);
INSERT INTO "ingredient" VALUES(2,'Томатный соус','г',3000,0.4);
INSERT INTO "ingredient" VALUES(3,'Пепперони','г',2000,1.2);
CREATE TABLE menu_category (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO "menu_category" VALUES(1,'Пицца');
INSERT INTO "menu_category" VALUES(2,'Напитки');
CREATE TABLE "order" (
	id INTEGER NOT NULL, 
	client_id INTEGER NOT NULL, 
	employee_id INTEGER NOT NULL, 
	courier_id INTEGER, 
	created_at DATETIME NOT NULL, 
	order_type VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	total_sum NUMERIC(12, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(client_id) REFERENCES client (id), 
	FOREIGN KEY(employee_id) REFERENCES employee (id), 
	FOREIGN KEY(courier_id) REFERENCES courier (id)
);
INSERT INTO "order" VALUES(1,1,2,NULL,'2024-05-01 12:30:00.000000','in_hall','closed',1020);
INSERT INTO "order" VALUES(2,2,2,1,'2024-05-02 18:00:00.000000','delivery','delivered',550);
CREATE TABLE order_item (
	id INTEGER NOT NULL, 
	order_id INTEGER NOT NULL, 
	dish_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	price_at_order NUMERIC(10, 2) NOT NULL, 
	wishes VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES "order" (id), 
	FOREIGN KEY(dish_id) REFERENCES dish (id)
);
INSERT INTO "order_item" VALUES(1,1,1,1,450,NULL);
INSERT INTO "order_item" VALUES(2,1,2,1,550,NULL);
INSERT INTO "order_item" VALUES(3,1,3,1,120,'без льда');
INSERT INTO "order_item" VALUES(4,2,2,1,550,NULL);
CREATE TABLE payment (
	id INTEGER NOT NULL, 
	order_id INTEGER NOT NULL, 
	payment_system_id INTEGER, 
	paid_at DATETIME NOT NULL, 
	amount NUMERIC(12, 2) NOT NULL, 
	method VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (order_id), 
	FOREIGN KEY(order_id) REFERENCES "order" (id), 
	FOREIGN KEY(payment_system_id) REFERENCES payment_system (id)
);
INSERT INTO "payment" VALUES(1,1,NULL,'2024-05-01 13:00:00.000000',1020,'card','paid');
INSERT INTO "payment" VALUES(2,2,1,'2024-05-02 18:05:00.000000',550,'online','paid');
CREATE TABLE payment_system (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	external_payment_id VARCHAR(100), 
	status VARCHAR(30), 
	PRIMARY KEY (id)
);
INSERT INTO "payment_system" VALUES(1,'ЮKassa','ext-123','success');
CREATE TABLE recipe (
	dish_id INTEGER NOT NULL, 
	ingredient_id INTEGER NOT NULL, 
	quantity NUMERIC(12, 3) NOT NULL, 
	PRIMARY KEY (dish_id, ingredient_id), 
	FOREIGN KEY(dish_id) REFERENCES dish (id), 
	FOREIGN KEY(ingredient_id) REFERENCES ingredient (id)
);
INSERT INTO "recipe" VALUES(1,1,150);
INSERT INTO "recipe" VALUES(1,2,100);
INSERT INTO "recipe" VALUES(2,1,150);
INSERT INTO "recipe" VALUES(2,3,80);
CREATE TABLE shift (
	id INTEGER NOT NULL, 
	employee_id INTEGER NOT NULL, 
	shift_date DATE NOT NULL, 
	start_time DATETIME NOT NULL, 
	end_time DATETIME, 
	role_in_shift VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(employee_id) REFERENCES employee (id)
);
INSERT INTO "shift" VALUES(1,2,'2024-05-01','2024-05-01 09:00:00.000000','2024-05-01 18:00:00.000000','официант');
INSERT INTO "shift" VALUES(2,1,'2024-05-01','2024-05-01 10:00:00.000000','2024-05-01 20:00:00.000000','повар');
CREATE TABLE supplier (
	id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	contact_person VARCHAR(150), 
	phone VARCHAR(20), 
	PRIMARY KEY (id)
);
INSERT INTO "supplier" VALUES(1,'ООО Молоко','Анна','+79009990000');
CREATE TABLE supply (
	id INTEGER NOT NULL, 
	supplier_id INTEGER NOT NULL, 
	supply_date DATE NOT NULL, 
	total_sum NUMERIC(12, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(supplier_id) REFERENCES supplier (id)
);
INSERT INTO "supply" VALUES(1,1,'2024-04-30',7000);
CREATE TABLE supply_line (
	id INTEGER NOT NULL, 
	supply_id INTEGER NOT NULL, 
	ingredient_id INTEGER NOT NULL, 
	quantity NUMERIC(12, 3) NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(supply_id) REFERENCES supply (id), 
	FOREIGN KEY(ingredient_id) REFERENCES ingredient (id)
);
INSERT INTO "supply_line" VALUES(1,1,1,5000,0.8);
INSERT INTO "supply_line" VALUES(2,1,2,3000,0.4);
COMMIT;
