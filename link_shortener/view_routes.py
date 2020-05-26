'''
Copyright (C) 2020 Link Shortener Authors (see AUTHORS in Documentation).
Licensed under the MIT (Expat) License (see LICENSE in Documentation).
'''
from decouple import config

from sanic import Blueprint
from sanic.response import html, json, redirect

from sanic_oauth.blueprint import login_required

from sqlalchemy.sql.expression import select as sql_select

from link_shortener.models import links, salts
from link_shortener.templates import template_loader

from link_shortener.core.decorators import credential_whitelist_check


view_blueprint = Blueprint('views')


@view_blueprint.route('/<link_endpoint>', methods=['GET'])
async def redirect_link(request, link_endpoint):
    try:
        async with request.app.engine.acquire() as conn:
            query = await conn.execute(
                links.select().where(
                    links.columns['endpoint'] == link_endpoint
                ).where(
                    links.columns['is_active'] == True
                )
            )
            link_data = await query.fetchone()
            if link_data.password is None:
                return redirect(link_data.url)

            return redirect('/authorize/{}'.format(link_data.id))

    except Exception:
        return json({'message': 'Link inactive or does not exist'}, status=404)


@view_blueprint.route('/', methods=['GET'])
async def landing_page(request):
    return redirect('/links/about', status=301)


@view_blueprint.route('/links/about', methods=['GET'])
async def about_page(request):
    try:
        return html(template_loader(template_file='about.html'), status=200)

    except Exception:
        return json({'message': 'Template failed loading'}, status=500)


@view_blueprint.route('/links/all', methods=['GET'])
@login_required
@credential_whitelist_check
async def all_active_links(request, user):
    try:
        async with request.app.engine.acquire() as conn:
            queryset = await conn.execute(links.select())
            data = await queryset.fetchall()
            return html(template_loader(
                            template_file='all_links.html',
                            domain_name=config('DOMAIN_NAME'),
                            data=data
                        ), status=200)

    except Exception:
        return json({'message': 'Template failed loading'}, status=500)


@view_blueprint.route('/links/me', methods=['GET'])
@login_required
@credential_whitelist_check
async def owner_specific_links(request, user):
    try:
        async with request.app.engine.acquire() as conn:
            queryset = await conn.execute(
                links.select().where(
                    links.columns['owner_id'] == user.id
                )
            )
            link_data = await queryset.fetchall()
            return html(template_loader(
                            template_file='my_links.html',
                            domain_name=config('DOMAIN_NAME'),
                            link_data=link_data
                        ), status=200)

    except Exception as error:
        print(error)
        return json({'message': 'Template failed loading'}, status=500)


@view_blueprint.route('/delete/<link_id>', methods=['GET'])
@login_required
@credential_whitelist_check
async def delete_link(request, user, link_id):
    try:
        async with request.app.engine.acquire() as conn:
            trans = await conn.begin()
            await conn.execute(
                links.delete().where(
                    links.columns['id'] == link_id
                )
            )
            await trans.commit()
            await trans.close()
            return redirect('/links/me', status=302)

    except Exception:
        await trans.close()
        return json({'message': 'Link does not exist'}, status=404)


@view_blueprint.route('/activate/<link_id>', methods=['GET'])
@login_required
@credential_whitelist_check
async def activate_link(request, user, link_id):
    try:
        async with request.app.engine.acquire() as conn:
            trans = await conn.begin()
            query = await conn.execute(
                links.select().where(
                    links.columns['id'] == link_id
                )
            )
            link_data = await query.fetchone()
            if link_data.is_active:
                return json({'message': 'Link is already active'}, status=400)

            await conn.execute(
                links.update().where(
                    links.columns['id'] == link_id
                ).values(is_active=True)
            )
            await trans.commit()
            await trans.close()
            return redirect('/links/me')

    except Exception:
        await trans.close()
        return json({'message': 'Link does not exist'}, status=404)


@view_blueprint.route('/deactivate/<link_id>', methods=['GET'])
@login_required
@credential_whitelist_check
async def deactivate_link(request, user, link_id):
    try:
        async with request.app.engine.acquire() as conn:
            trans = await conn.begin()
            query = await conn.execute(
                links.select().where(
                    links.columns['id'] == link_id
                )
            )
            link_data = await query.fetchone()
            if not link_data.is_active:
                return json(
                    {'message': 'Link is already inactive'},
                    status=400
                )

            await conn.execute(
                links.update().where(
                    links.columns['id'] == link_id
                ).values(is_active=False)
            )
            await trans.commit()
            await trans.close()
            return redirect('/links/me')

    except Exception:
        await trans.close()
        return json({'message': 'Link does not exist'}, status=404)


@view_blueprint.route('/reset/<link_id>', methods=['GET'])
@login_required
@credential_whitelist_check
async def reset_password_view(request, user, link_id):
    try:
        async with request.app.engine.acquire() as conn:
            trans = await conn.begin()
            query = await conn.execute(
                links.select().where(
                    links.columns['id'] == link_id
                )
            )
            link_data = await link_query.fetchone()
            await conn.execute(
                links.update().where(
                    links.columns['id'] == link_id
                ).values(
                    password=None
                )
            )
            await conn.execute(
                salts.delete().where(
                    salts.columns['identifier'] == link_data.identifier
                )
            )
            await trans.commit()
            await trans.close()
            return redirect('/links/me')

    except Exception:
        await trans.close()
        return json({'message': 'link does not exist'}, status=404)
