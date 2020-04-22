'''
Copyright (C) 2020 Link Shortener Authors (see AUTHORS in Documentation).
Licensed under the MIT (Expat) License (see LICENSE in Documentation).
'''
import uuid

from sanic import Blueprint
from sanic.response import redirect, html, json

from sanic_oauth.blueprint import login_required

from sanic_wtf import SanicForm

from sqlalchemy.exc import InvalidRequestError

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from initialise_db import initdb_blueprint


form_blueprint = Blueprint('forms')

actives = initdb_blueprint.active_table
inactives = initdb_blueprint.inactive_table


class CreateForm(SanicForm):
    endpoint = StringField('Endpoint', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('Create')


class UpdateForm(SanicForm):
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('Update')


@form_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
async def create_link(request, user):
    form = CreateForm(request)
    if (request.method == 'POST') and form.validate():
        data = [(
            str(uuid.uuid1())[:36],
            user.email,
            user.id,
            form.endpoint.data,
            form.url.data
        )]
        try:
            async with request.app.engine.acquire() as conn:
                trans = await conn.begin()
                await conn.execute(
                    'INSERT INTO active_links \
                     (identifier, owner, owner_id, endpoint, url) \
                     VALUES (%s, %s, %s, %s, %s)',
                    data
                )
                await trans.commit()
                await trans.close()
                return redirect('/links/me')

        except InvalidRequestError:
            try:
                await conn.execute(
                    'INSERT INTO inactive_links \
                     (identifier, owner, owner_id, endpoint, url) \
                     VALUES (%s, %s, %s, %s, %s)',
                    data
                )
                await trans.commit()
                await trans.close()
                return json(
                    {'message': 'endpoint already exists, created inactive'},
                    status=201
                    )
            except Exception:
                await trans.close()
                return json(
                    {'message': 'creating a new link failed'},
                    status=500
                )

    content = f"""
    <div class="container">
    <form action="" method="POST">
      <h1 id="form-header">Create a new link</h1>
      {'<br>'.join(form.csrf_token.errors)}
      {form.csrf_token}
      {'<br>'.join(form.endpoint.errors)}
      <br>
      <ul>
      <li>{form.endpoint(size=20, placeholder="Endpoint")}</li>
      <li>{form.url(size=20, placeholder="URL")}</li>
      <li>{form.submit}</li>
      </ul>
    </form>
    """
    base = open('src/templates/base.html', 'r').read()
    appendix = open('src/templates/forms/create_form.html', 'r').read()

    return html(base + content + appendix)


@form_blueprint.route('/edit/active/<link_id>', methods=['GET', 'POST'])
@login_required
async def update_active_link(request, user, link_id):
    form = UpdateForm(request)
    if (request.method == 'POST') and form.validate():
        try:
            async with request.app.engine.acquire() as conn:
                trans = await conn.begin()
                await conn.execute(
                    'UPDATE active_links SET url = %s \
                     WHERE id = %s',
                    [(form.url.data, link_id)]
                )
                await trans.commit()
                await trans.close()
                return redirect('/links/me')

        except Exception:
            await trans.close()
            return json({'message': 'updating link failed'}, status=500)

    try:
        async with request.app.engine.acquire() as conn:
            query = await conn.execute(
                actives.select().where(
                    actives.columns['id'] == link_id
                )
            )
            row = await query.fetchone()

            content = f"""
            <div class="container">
            <form action="" method="POST">
              <h1 id="form-header">/{row.endpoint}</h1>
              {'<br>'.join(form.csrf_token.errors)}
              {form.csrf_token}
              {'<br>'.join(form.url.errors)}
              <br>
              <ul>
              <li>{form.url(size=50, placeholder=row.url)}</li>
              <li>{form.submit}</li>
              </ul>
            </form>
            """
            base = open('src/templates/base.html', 'r').read()
            appendix = open('src/templates/forms/create_form.html', 'r').read()

            return html(base + content + appendix)

    except Exception:
        return json({'message': 'getting update form failed'}, status=500)


@form_blueprint.route('/edit/inactive/<link_id>', methods=['GET', 'POST'])
@login_required
async def update_inactive_link(request, user, link_id):
    form = UpdateForm(request)
    if (request.method == 'POST') and form.validate():
        try:
            async with request.app.engine.acquire() as conn:
                trans = await conn.begin()
                await conn.execute(
                    'UPDATE inactive_links SET url = %s \
                     WHERE id = %s',
                    [(form.url.data, link_id)]
                )
                await trans.commit()
                await trans.close()
                return redirect('/links/me')

        except Exception:
            await trans.close()
            return json({'message': 'updating link failed'}, status=500)

    try:
        async with request.app.engine.acquire() as conn:
            query = await conn.execute(
                inactives.select().where(
                    inactives.columns['id'] == link_id
                )
            )
            row = await query.fetchone()

            content = f"""
            <div class="container">
            <form action="" method="POST">
              <h1 id="form-header">/{row.endpoint}</h1>
              {'<br>'.join(form.csrf_token.errors)}
              {form.csrf_token}
              {'<br>'.join(form.url.errors)}
              <br>
              <ul>
              <li>{form.url(size=50, placeholder=row.url)}</li>
              <li>{form.submit}</li>
              </ul>
            </form>
            """
            base = open('src/templates/base.html', 'r').read()
            appendix = open('src/templates/forms/create_form.html', 'r').read()

            return html(base + content + appendix)

    except Exception:
        return json({'message': 'getting update form failed'}, status=500)