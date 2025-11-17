create database txt_to_sql;
use txt_to_sql;

select * from customers;
select * from sales_order;

-- TOTAL LINE TOTAL FOR GEISS COMPANY 
select s.`Customer Name Index`, sum(s.`Line Total`)from customers c, sales_order s 
where c.`Customer Index` = s.`Customer Name Index`
and c.`Customer Names` = 'Geiss Company'
group by s.`Customer Name Index`;