database tables:

1) Users table has following column
- id(primary_key,auto_increment)
- name
- email
- username
- password
- balance
-timestamp

2) Transactions table has following column
-tid(primary_key, auto_increment)
-tuid(foreign key references Users(id))
-company name
-company symbol
-quantity
-lastprice
-total
-timestamp

3) Stocks table has following column

- sid(primary_key,auto_increment)
- suid(foreign_key references Users(id))
- company name
- company symbol
- schange

Error-handling
1) connection
2) buy-sell
3) ticker symbol