# vexturPLM
#### Video demo: https://youtu.be/CtsuoKEou8I
#### Description:

## Main idea

__A PLM is a term in manufacturing that refers to the process of managing the entire lifecycle of a product.__

Usually, PLM systems are very expensive, and this is exactly why I wanted to make a system that helps small businesses and hobbyists organise their projects.

## Setting up

I will be presenting how you set up this website using bash, but using cmd is also similar.

First, run this to create the virtual env:

```bash
    python3 -m venv venv
```

After the env was created, run:

```bash
    source ./venv./Scripts/activate
```

Now, you need to install the python dependencies, using pip:

```bash
    pip install -r requirements.txt
```

To finish setup, you will have to also create the database and a default user:

```bash
    python3 init.py
```

You are now all set! To run the project, run this command:

```bash
    python3 app.py
```

## Logging in

### Logging in the temporary account

On the home page, click on the _log in_ button. You will be redirected to a login page, type the following data in the fields:

1. __USERNAME: admin__
2. __PASSWORD: admin__

After you click _log in_, you should be logged in the admin account.

### Creating accounts

After you logged in, you can create accounts by clicking on _Create_ __->__ _User_.

Next, complete your fields like in the example below:

1. __Full name: Filip Pernea__ - the full name of the user that will own the account (__required__)
2. __Username: filip-pernea__ - if you are creating many accounts, its better to make this "(_first name_)-(_last name_)". (__required__)
3. __Password: example1234__ - set this as a strong password! (__required__)
4. __Role: 255__ - role is currently only used for the ability to create users (_only people with role 255_), please make sure at least one account can create new users. (__required__)

After you've inputted the data, click on _Create_ to create the account.

__YOU WILL NOT BE AUTOMATICALLY LOGGED IN TO THIS ACCOUNT!__

### Deleting the temporary account

You can delete the temporary account by clicking on the _Delete your account __here__!_ text.

## Learning how to use the website

This section is made to show how you can use the website as easily as possible, but also explains everything there is to know about a PLM.

### Logging in

After you set up the website, and actually visit it, you will see the home page. On the home page, click the _log in_ text, and input your account username and password.

__In order to visit the rest of the website you must be logged in!__

### Creating an ECO

First of all, in order to create anything, you need to __create a ECO__. Creating an ECO helps with tracabilty, and that is exactly why you should always group your ECOs, like in the example below:

1. __ECO000001: Initial commit ECO__ - in this ECO we create parts we have in stock, like screws, nuts, generally parts we use in our projects
2. __ECO000002: Adding project files__ - in this ECO we create parts that are full on projects, like __ASSY000001: Robot assembly__, but also BOMs for the parts we added.
3. __ECO000003: Adding parts we just purchased__ - we add some other parts we want to use.

To create an ECO, simply click the _Create_ button and then the _ECO_ button. You will be redirected to a page where you will add the ECO description, and the ECO number will be automatically generated.

After you create the ECO, you will be redirected to the ECO page where you can create new changes. You can always revisit this page by clicking on _Modify_ __->__ _Pending ECO_ or _View_ __->__ _ECOs_, and then selecting your ECO.

### Creating parts

__You can only create parts from an ECO!__

After you've created an ECO, you can create a part by clicking on _Add change_. The create part menu will appear.

Input your info, like in the example below:

1. __Part number: ASSY000001__ - Unique identifier of that part. (__required__)
2. __Description: Battery assembly__ - A short description of the part, usually less than 30-40 characters. (__required__)
3. __Internal revision: 1__ - Automatically set, will increment once you modify that part in another ECO. (__required__)
4. __Internal ECO: ECO000001__ - Automatically set, will change once you modify that part in another ECO. (__required__)
5. __Customer revition: none__ - Optional, only needed if you are a manufacturer making products for other people. (__optional__)
6. __Customer ECO: none__ - Optional, only needed if you are a manufacturer making products for other people. (__optional__)
7. __Type: Manufactured__ - Four types of parts: _manufactured_(you will be able to set a __BOM__), _purchased_(you will be able to set a __manufacturer__ and __MPN__), _document_ and _level_(used only for grouping things in the BOM), (__required__)
8. __IN OUR CASE: BOM: BOM000001__ - Identifier for the BOM of that part. (__required__)

After you've finished inputting the data, click on the _Add change_ button, and you will be redirected to the ECO page.

### Modify parts

__You can only modify parts from an ECO!__

After you've created an ECO, you can modify a part by clicking on _Add change_ __->__ _Modify part_.

Check that the part you want to modify actually exists. You might find it helpful to open the PLM in a new tab and click on _View_ __->__ _Parts_.

Input the data, like in the example below:

1. __Part number: ASSY000001__ - Part number of the part you want to modify. (__required__)
2. __Value to change: Description__ - You can change everything except the _internal revision_, _internal ECO_, _part number_ and _type_. (__required__)
3. __Change value to: 3V Battery assembly__ - New value (__required__)

After you've finished inputting the data, click on the _Add change_ button, and you will be redirected to the ECO page.

### Adding a new BOM item

_A BOM (__Bill of materials__) is a list of parts that are used in order to make that part._

__You can only create a BOM item from an ECO!__

After you've created an ECO, you can add a new BOM item by clicking on _Add change_ __->__ _New BOM item_.

Check that the part you want to add to the BOM actually exists. You might find it helpful to open the PLM in a new tab and click on _View_ __->__ _Parts_.

Input the data, like in the example below:

1. __BOM: BOM000002__ - BOM number of the BOM you want to add the part to. (__required__)
2. __Part number: ASSY000001__ - part number of the part that you want to be added to the BOM. (__required__)
3. __Quantity: 1__ - quantity of the part. (__required__)

After you've finished inputting the data, click on the _Add change_ button, and you will be redirected to the ECO page.

### Modifying a BOM item

__You can only modify a BOM item from an ECO!__

After you've created an ECO, you can modify a BOM item by clicking on _Add change_ __->__ _Modify BOM item_.

Check that the item you want to modify is in the BOM. You might find it helpful to open the PLM in a new tab and click on _View_ __->__ _BOMs_.

Input the data, like in the example below:

1. __BOM: BOM000002__ - BOM number of the BOM that has the item you want to edit. (__required__)
2. __Part number: ASSY000001__ - part number of the part that you want to edit to the BOM. (__required__)
3. __New quantity: 10__ - new quantity of the part. (__required__)

After you've finished inputting the data, click on the _Add change_ button, and you will be redirected to the ECO page.

### Deleting a BOM item

__You can only delete a BOM item from an ECO!__

After you've created an ECO, you can delete a BOM item by clicking on _Add change_ __->__ _Delete BOM item_.

Check that the item you want to delete is in the BOM. You might find it helpful to open the PLM in a new tab and click on _View_ __->__ _BOMs_ __->__ _(__your BOM__)_.

Input the data, like in the example below:

1. __BOM: BOM000001__ - BOM number that has the item you want to delete. (__required__)
2. __Part number: ASSY000001__ - part number of the item you want to delete. (__required__)

After you've finished inputting the data, click on the _Add change_ button, and you will be redirected to the ECO page.

### Viewing ECOs, parts and BOMs

You can view parts by clicking on _View_ __->__ _Parts_.

You can view ECOs by clicking on _View_ __->__ _ECOs_.

You can view BOMs by clicking on _View_ __->__ _BOMs_.

## Understanding the code

This section is made to simply explain what eacj code file does.

### app.py file

The _app.py_ file is the main file of the project and includes the code for each of the routes of the websites, not much to explain here.

### functions.py file

The _functions.py_ file includes functions for checking passwords and checking log in status on page load.

### init.py file

The _init.py_ file includes code for creating the database and adding the default user.

### schema.sql file

The _schema.sql_ file includes SQL queries for making the database.
