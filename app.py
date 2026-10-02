from flask import Flask, redirect, render_template, url_for, request, session, flash, g, jsonify
from flask_session import Session
from functions import login_required, hash_password, check_password, check_characters_username, check_characters_password
import sqlite3

from settings import PART_TYPE_VALUES, PART_UM_VALUES, CHANGE_TYPE_STYLE, CHANGE_VALUE_STYLE, ECO_CHANGE_VALUE_VALUES

# Configure app
app = Flask(__name__)
application = app

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure jinja filters
def upcase(s):
    try:
        return s.upper()
    except:
        return ""

app.jinja_env.filters["upper"] = upcase

# Setup database
DATABASE = "database.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Access columns by name

        db.execute('PRAGMA journal_mode=WAL;') # Enable WAL logic
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    """Basic index route"""
    if session.get("user_id"):
        db = get_db()
        name = db.execute("SELECT * FROM users WHERE id = ?", [session.get("user_id")]).fetchone()["full_name"]
        return render_template("index.html", full_name=name)
    else:
        return render_template("index.html")

@app.route("/contact")
def contact():
    """Basic contact route"""
    return render_template("contact.html")

###############
# USER ROUTES #
###############

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log the user in"""
    if request.method == "POST":
        db = get_db()

        username = request.form.get("username")
        password = request.form.get("password")

        if not password or not username:
            flash("You did not provide a username and/or password.", "error")
            return render_template("login.html", username=username)
        
        if not check_characters_password(password) or not check_characters_username(username):
            flash("Password is not correct or user does not exist.", "error")
            return render_template("login.html", username=username)

        user = db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchone()

        if user and check_password(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash(f"You are now logged in as {user["full_name"]}.", "success")
            return redirect("/")
        else:
            flash("Password is not correct or user does not exist.", "error")
            return render_template("login.html", username=username)
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Log the user out"""
    session.clear()
    flash("You are now logged out.", "success")
    return redirect("/")

@app.route("/profile/<user>")
@login_required
def profile(user):
    db = get_db()
    try:
        username = db.execute("SELECT * FROM users WHERE id = ?", [int(user)]).fetchone()["username"]

        if not username:
            flash("User not found.", "error")
            return redirect("/")

        return redirect(url_for("profile", user=username))
    except:
        user = db.execute("SELECT * FROM users WHERE username = ?", [user]).fetchone()

    if not user or len(user) == 0:
        flash("User not found.", "error")
        return redirect("/")

    return render_template("profile.html", user=user)

@app.route("/deleteuser")
@login_required
def delete_user():
    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", [session["user_id"]])
    db.commit()
    session.clear()
    return redirect("/")

#################
# CREATE ROUTES #
#################

@app.route("/create/eco", methods=["GET", "POST"])
@login_required
def create_eco():
    if request.method == "POST":
        db = get_db()
        description = request.form.get("description")

        if not description:
            flash("You did not provide a description.", "error")
            return redirect("/create/eco")

        last_eco = db.execute("SELECT * FROM eco ORDER BY created_at DESC LIMIT 1").fetchone()

        if last_eco:
            new_eco_number = last_eco["id"] + 1
            new_eco = f"ECO{new_eco_number:06}"
        else:
            new_eco = "ECO000001"

        db.execute("INSERT INTO eco (eco, description) VALUES (?, ?)", [new_eco, description])
        db.commit()

        flash(f"ECO {new_eco}: \"{description}\" created.", "success")
        return redirect(f"/eco/{new_eco}")
    else:
        return render_template("create_eco.html")

@app.route("/create/user", methods=["GET", "POST"])
@login_required
def create_user():
    """Log the user in"""
    db = get_db()
    
    if request.method == "POST":
        full_name = request.form.get("full_name")
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if not full_name or not password or not username or not role:
            flash("You did not provide a username and/or password.", "error")
            return redirect("/create/user")
        
        if not check_characters_password(password) or not check_characters_username(username):
            flash("Requirements not met.", "error")
            return redirect("/create/user")

        try:
            db.execute("INSERT INTO users (full_name, bio, username, password, role) VALUES (?, ?, ?, ?, ?)", [full_name, "", username, hash_password(password), role])
            db.commit()
            flash("Account created!", "success")
            return redirect("/")
        except:
            flash("Role is not a number", "error")
            return redirect("/")
    else:
        user = db.execute("SELECT * FROM users WHERE id = ?", [session["user_id"]]).fetchone()
        if user["role"] != 255:
            flash("You don't have the permission to create accounts!")
            return redirect("/")
        return render_template("create_account.html")

###############
# PART ROUTES #
###############

@app.route("/part")
@login_required
def part_main():
    db = get_db()
    parts = db.execute("SELECT * FROM parts ORDER BY pn").fetchall()

    return render_template("parts.html", parts=parts)

@app.route("/part/<part_nr>")
@login_required
def part(part_nr):
    db = get_db()
    part = db.execute("SELECT * FROM parts WHERE pn = ?", [part_nr]).fetchone()

    if not part:
        flash(f"Part not found.", "error")
        return redirect("/")
    
    return render_template("part_info.html", part=part)

##############
# BOM ROUTES #
##############

@app.route("/bom")
@login_required
def bom_main():
    db = get_db()
    boms = db.execute("SELECT bom, COUNT(component_pn) AS count FROM bom GROUP BY bom").fetchall()

    return render_template("bom.html", boms=boms)

@app.route("/bom/<bom_nr>")
@login_required
def bom(bom_nr):
    db = get_db()

    parts = db.execute("SELECT * FROM bom WHERE bom = ?", [bom_nr]).fetchall()

    if not parts:
        flash(f"BOM not found.", "error")
        return redirect("/")
    
    return render_template("bom_view.html", bom=bom_nr, parts=parts)

##############
# ECO ROUTES #
##############

@app.route("/eco")
@login_required
def eco_main():
    db = get_db()
    ecos = db.execute("SELECT * FROM eco ORDER BY created_at").fetchall()
    return render_template("eco.html", title="ECOs", ecos=ecos)

@app.route("/eco/pending")
@login_required
def eco_pending():
    db = get_db()
    ecos = db.execute("SELECT * FROM eco WHERE status = ? ORDER BY created_at", ["pending"]).fetchall()
    return render_template("eco.html", title="Pending ECOs", ecos=ecos)

@app.route("/eco/<eco_nr>")
@login_required
def eco(eco_nr):
    db = get_db()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash(f"ECO not found.", "error")
        return redirect("/")
    
    changes = db.execute("SELECT * FROM changes WHERE eco = ? ORDER BY id", [eco_nr]).fetchall()

    last_pn = None

    changes_new = []

    for change in changes:
        row = dict(change)
        if change["object_changed"] == last_pn:
            row["type"] = ""
            row["object_changed"] = ""
        else:
            last_pn = change["object_changed"]
        row["type"] = CHANGE_TYPE_STYLE[row["type"]]
        row["value_changed"] = CHANGE_VALUE_STYLE[row["value_changed"]]
        changes_new.append(row)

    if eco["status"] == "pending":
        return render_template("eco_edit.html", eco=eco_nr, changes=changes_new)
    else:
        return render_template("eco_info.html", eco=eco_nr, changes=changes_new)
    
@app.route("/eco/<eco_nr>/<change_id>")
@login_required
def eco_change(eco_nr, change_id):
    db = get_db()
    change = db.execute("SELECT * FROM changes WHERE eco = ? AND id = ?", [eco_nr, change_id]).fetchone()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "released":
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")

    if not change:
        flash("Change not found.", "error")
        return redirect("/")

    return render_template("change_edit.html", eco=eco_nr, change=change)

@app.route("/eco/<eco_nr>/<change_id>/delete")
@login_required
def eco_change_delete(eco_nr, change_id):
    db = get_db()
    change = db.execute("SELECT * FROM changes WHERE eco = ? AND id = ?", [eco_nr, change_id]).fetchone()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "released":
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")

    if not change:
        flash("Change not found.", "error")
        return redirect("/")
    
    db.execute("DELETE FROM changes WHERE eco = ? AND id = ?", [eco_nr, change_id])

    db.commit()

    return redirect("/")

@app.route("/eco/<eco_nr>/create")
@login_required
def eco_new_change(eco_nr):
    db = get_db()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "pending":
        return render_template("eco_add_change.html", eco=eco["eco"])
    else:
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")
    
@app.route("/eco/<eco_nr>/new_part", methods=["POST"])
@login_required
def eco_new_part(eco_nr):
    db = get_db()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "released":
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")
    
    pn = request.form.get("part_number")
    desc = request.form.get("description")
    int_rev = 1
    int_eco = eco_nr
    cust_rev = request.form.get("cust_revision")
    cust_eco = request.form.get("cust_eco")
    part_type = request.form.get("type")
    bom = request.form.get("bom")
    manuf = request.form.get("manufacturer")
    mpn = request.form.get("mpn")
    um = request.form.get("um")

    if len(db.execute("SELECT * FROM parts WHERE pn = ?", [pn]).fetchall()) > 0:
        flash("Part with this PN already exists.", "error")
        return render_template("eco_add_change.html", eco=eco_nr, desc=desc, cust_rev=cust_rev, cust_eco=cust_eco, bom=bom, manuf=manuf, mpn=mpn)

    if not (pn and desc and int_rev and part_type and part_type in PART_TYPE_VALUES and um in PART_UM_VALUES):
        flash("You did not complete all required fields.", "error")
        return render_template("eco_add_change.html", eco=eco_nr, pn=pn, desc=desc, cust_rev=cust_rev, cust_eco=cust_eco, bom=bom, manuf=manuf, mpn=mpn)

    if part_type == "purchased" and not (manuf and mpn):
        flash("You did not complete all required fields.", "error")
        return render_template("eco_add_change.html", eco=eco_nr, pn=pn, desc=desc, cust_rev=cust_rev, cust_eco=cust_eco, bom=bom, manuf=manuf, mpn=mpn)

    db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
               [eco_nr, "part_create", pn, "pn", None, pn])
    db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
               [eco_nr, "part_create", pn, "description", None, desc])
    db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
               [eco_nr, "part_create", pn, "internal_revision", None, int_rev])
    db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
               [eco_nr, "part_create", pn, "internal_eco", None, eco_nr])
    if cust_rev:
        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "part_create", pn, "customer_revision", None, cust_rev])
    if cust_eco:
        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "part_create", pn, "customer_eco", None, cust_eco])
    db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
               [eco_nr, "part_create", pn, "type", None, part_type])
    db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
               [eco_nr, "part_create", pn, "unit", None, um])
    if part_type == "manufactured" and bom:
        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "part_create", pn, "bom", None, bom])
    if part_type == "purchased":
        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "part_create", pn, "manufacturer", None, manuf])
        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "part_create", pn, "mpn", None, mpn])
    
    db.commit()
    return redirect(f"/eco/{eco_nr}")

@app.route("/eco/<eco_nr>/modify_part", methods=["POST"])
@login_required
def eco_modify_part(eco_nr):
    db = get_db()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "released":
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")
    
    pn = request.form.get("pn")
    value_to_change = request.form.get("value")
    new_value = request.form.get("new")

    part = db.execute("SELECT * FROM parts WHERE pn = ?", [pn]).fetchone()

    if not (pn and value_to_change in ECO_CHANGE_VALUE_VALUES and new_value):
        flash("You did not complete all required fields.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    if (part["type"] == "manufactured" or part["type"] == "document" or part["type"] == "level") and (value_to_change == "manufacturer" or value_to_change == "mpn"):
        flash("You cannot change that value.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    if (part["type"] == "purchased" or part["type"] == "document" or part["type"] == "level") and value_to_change == "bom":
        flash("You cannot change that value.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    if len(db.execute("SELECT * FROM changes WHERE eco = ? AND object_changed = ? AND value_changed = ?", [eco_nr, pn, value_to_change]).fetchall()) > 0:
        flash("This value is already changed in this ECO.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    if len(db.execute("SELECT * FROM changes WHERE eco = ? AND type = ? AND object_changed = ?", [eco_nr, "part_create", pn]).fetchall()) > 0:
        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "part_create", pn, value_to_change, None, new_value])
    elif len(db.execute("SELECT * FROM parts WHERE pn = ?", [pn]).fetchall()) > 0:
        old_value = db.execute("SELECT * FROM parts WHERE pn = ?", [pn]).fetchone()[value_to_change]

        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "part_modify", pn, value_to_change, old_value, new_value])
    else:
        flash("Part not found.", "error")
        return redirect(f"/eco/{eco_nr}")

    db.commit()
    return redirect(f"/eco/{eco_nr}")

@app.route("/eco/<eco_nr>/new_bom_item", methods=["POST"])
@login_required
def eco_new_bom_item(eco_nr):
    db = get_db()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "released":
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")
    
    bom = request.form.get("bom")
    pn = request.form.get("pn")
    qty = request.form.get("qty")

    if not (bom and pn and qty):
        flash("You did not complete all required fields.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    if len(db.execute("SELECT * FROM bom WHERE bom = ? AND component_pn = ?", [bom, pn]).fetchall()) > 0 or len(db.execute("SELECT * FROM changes WHERE eco = ? AND type = ? AND object_changed = ?", [eco_nr, "bom_item_create", f"{bom}.{pn}"]).fetchall()) > 0:
        flash("BOM item already exists.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    if len(db.execute("SELECT * FROM changes WHERE eco = ? AND type = ? AND object_changed = ?", [eco_nr, "part_create", pn]).fetchall()) > 0 or len(db.execute("SELECT * FROM parts WHERE pn = ?", [pn]).fetchall()) > 0:
        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "bom_item_create", f"{bom}.{pn}", "quantity", None, qty])
    else:
        flash("Part not found.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    db.commit()
    return redirect(f"/eco/{eco_nr}")

@app.route("/eco/<eco_nr>/modify_bom_item", methods=["POST"])
@login_required
def eco_modify_bom_item(eco_nr):
    db = get_db()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "released":
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")
    
    bom = request.form.get("bom")
    pn = request.form.get("pn")
    qty = request.form.get("qty")

    if not (bom and pn and qty):
        flash("You did not complete all required fields.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    if len(db.execute("SELECT * FROM parts WHERE pn = ?", [pn]).fetchall()) > 0 and len(db.execute("SELECT * FROM bom WHERE bom = ? AND pn = ?", [bom, pn]).fetchall()) > 0:
        old_value = db.execute("SELECT * FROM bom WHERE bom = ? AND pn = ?", [bom, pn]).fetchall()["quantity"]
        
        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "bom_item_create", f"{bom}.{pn}", "quantity", old_value, qty])
    else:
        flash("Part not found.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    db.commit()
    return redirect(f"/eco/{eco_nr}")

@app.route("/eco/<eco_nr>/delete_bom_item", methods=["POST"])
@login_required
def eco_delete_bom_item(eco_nr):
    db = get_db()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "released":
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")
    
    bom = request.form.get("bom")
    pn = request.form.get("pn")

    if not (bom and pn):
        flash("You did not complete all required fields.", "error")
        return redirect(f"/eco/{eco_nr}")
    
    if len(db.execute("SELECT * FROM bom WHERE bom = ? AND component_pn = ?", [bom, pn]).fetchall()) > 0:
        old_value = db.execute("SELECT * FROM bom WHERE bom = ? AND component_pn = ?", [bom, pn]).fetchone()["quantity"]

        db.execute("INSERT INTO changes (eco, type, object_changed, value_changed, original_value, new_value) VALUES (?, ?, ?, ?, ?, ?)", 
                   [eco_nr, "bom_item_delete", f"{bom}.{pn}", "quantity", old_value, 0])
    else:
        flash("BOM not found.", "error")
        return redirect(f"/eco/{eco_nr}")

    db.commit()
    return redirect(f"/eco/{eco_nr}")

@app.route("/eco/<eco_nr>/release", methods=["POST"])
@login_required
def eco_release(eco_nr):
    db = get_db()
    eco = db.execute("SELECT * FROM eco WHERE eco = ?", [eco_nr]).fetchone()

    if not eco:
        flash("ECO not found.", "error")
        return redirect("/")
        
    if eco["status"] == "released":
        flash("You can't change this ECO. You can only change pending ECOs.", "error")
        return redirect("/")
    
    parts_to_create = {}

    changes = db.execute("SELECT * FROM changes WHERE eco = ?", [eco_nr]).fetchall()

    # we get each part and add a key-value pair to the dict with the KEY = PART_NUMBER, and VALUE = list of things we add.
    # after that, we just check if the type of the part has all the things it needs, and none of the things it doesn't.

    for change in changes:
        if change["type"] == "part_create":
            try:
                parts_to_create[change["object_changed"]][change["value_changed"]] = change["new_value"]
            except:
                parts_to_create[change["object_changed"]] = {}
                parts_to_create[change["object_changed"]][change["value_changed"]] = change["new_value"]
        elif change["type"] == "part_modify" and change["value_changed"] in ECO_CHANGE_VALUE_VALUES:
            int_rev = db.execute("SELECT * FROM parts WHERE pn = ?", [change["object_changed"]]).fetchone()["internal_revision"]

            db.execute(f"UPDATE parts SET {change["value_changed"]} = ?, internal_revision = ?, internal_eco = ? WHERE pn = ?", [change["new_value"], (int_rev + 1), change["eco"], change["object_changed"]])
        elif change["type"] == "bom_item_create" and change["value_changed"] in ECO_CHANGE_VALUE_VALUES:
            split = change["object_changed"].split(".")
            bom = split[0]
            pn = split[1]

            db.execute("INSERT INTO bom (bom, component_pn, quantity) VALUES (?, ?, ?)", [bom, pn, change["new_value"]])
        elif change["type"] == "bom_item_modify" and change["value_changed"] in ECO_CHANGE_VALUE_VALUES:
            split = change["object_changed"].split(".")
            bom = split[0]
            pn = split[1]

            db.execute("UPDATE bom SET quantity = ? WHERE bom = ? AND component_pn = ?", [change["new_value"], bom, pn])
        elif change["type"] == "bom_item_delete" and change["value_changed"] in ECO_CHANGE_VALUE_VALUES:
            split = change["object_changed"].split(".")
            bom = split[0]
            pn = split[1]

            db.execute("DELETE FROM bom WHERE bom = ? AND component_pn = ?", [bom, pn])

    for pn, part in parts_to_create.items():
        if not (part["description"] and part["internal_revision"] and part["internal_eco"] and part["type"] and part["unit"]):
            flash("An error occurred.", "error")
            return redirect(f"/eco/{eco_nr}")
        
        if part["type"] == "manufactured":
            if not part["bom"]:
                flash("An error occurred.", "error")
                return redirect(f"/eco/{eco_nr}")
            else:
                db.execute("INSERT INTO parts (pn, description, internal_revision, internal_eco, customer_revision, customer_eco, type, unit, bom) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           [pn, part["description"], part["internal_revision"], part["internal_eco"], part.get("customer_revision"), part.get("customer_eco"), part["type"], part["unit"], part["bom"]])
        elif part["type"] == "purchased":
            if not (part["manufacturer"] and part["mpn"]):
                flash("An error occurred.", "error")
                return redirect(f"/eco/{eco_nr}")
            else:
                db.execute("INSERT INTO parts (pn, description, internal_revision, internal_eco, customer_revision, customer_eco, type, unit, manufacturer, mpn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           [pn, part["description"], part["internal_revision"], part["internal_eco"], part.get("customer_revision"), part.get("customer_eco"), part["type"], part["unit"], part["manufacturer"], part["mpn"]])
        else:
            db.execute("INSERT INTO parts (pn, description, internal_revision, internal_eco, customer_revision, customer_eco, type, unit, manufacturer, mpn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       [pn, part["description"], part["internal_revision"], part["internal_eco"], part["customer_revision"], part["customer_eco"], part["type"], part["unit"], part["manufacturer"], part["mpn"]])

    db.execute("UPDATE eco SET status = ? WHERE eco = ?", ["released", eco_nr])

    db.commit()
    return redirect(f"/eco/{eco_nr}")

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
