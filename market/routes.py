from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, Loginform, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
#ensure user is logged in
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()

    if request.method == "POST":
        #Purchase item function
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                #p_item_object.owner = current_user.id
                #current_user.budget -= p_item_object.price
                #db.session.commit()
                flash(f'Success! You purchased: {p_item_object.name}', category='success')
            else:
                flash(f'Not enough fund! For: {p_item_object.name}!', category='danger')

        #Selling item
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            #ensure he owns the object
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f'Success! You sold: {s_item_object.name}', category='success')
            else:
                flash(f'Not able to sell item: {s_item_object.name}!', category='danger')

        return redirect(url_for('market_page'))
    if request.method == "GET":
        #only item without owner
        #items = Item.query.all()
        items = Item.query.filter_by(owner=None)
        #relation between user and item is by id
        owned_items = Item.query.filter_by(owner=current_user.id)

        total_price = sum(item.price for item in owned_items)

        return render_template('market.html', items=items, purchase_form=purchase_form,
                               owned_items=owned_items, selling_form=selling_form, total_price=total_price)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Success! You are logged in as: {user_to_create.username}', category='success')

        return redirect(url_for('market_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Error : {err_msg}', 'danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = Loginform()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password not matching! try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You have been logged out', category='info')
    return redirect(url_for("home_page"))
