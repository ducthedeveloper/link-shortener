'''
Copyright (C) 2020 Link Shortener Authors (see AUTHORS in Documentation).
Licensed under the MIT (Expat) License (see LICENSE in Documentation).
'''
import uuid

from datetime import date
from decouple import config
from json import loads

from sanic import Blueprint
from sanic.response import json

from link_shortener.models import actives


api_create_delete_blueprint = Blueprint('create_delete')


@api_create_delete_blueprint.route('/api/links', methods=['POST'])
async def api_create_link(request):
    try:
        token = request.headers['Bearer']
        if (token != config('ACCESS_TOKEN')):
            return json({'message': 'Unauthorized'}, status=401)

    except KeyError:
        return json({'message': 'Please provide a token'}, status=400)

    try:
        payload = loads(request.body)

        owner = payload['owner']
        owner_id = payload['owner_id']
        endpoint = payload['endpoint']
        url = payload['url']

        sd_data = payload['switch_date']
        switch_date = date(sd_data['Year'], sd_data['Month'], sd_data['Day'])

    except KeyError:
        return json({'message': 'Please provide all data'}, status=400)

    except Exception:
        return json({'message': 'Incorrect payload'}, status=400)

    try:
        async with request.app.engine.acquire() as conn:
            trans = await conn.begin()
            identifier = str(uuid.uuid1())
            try:
                await conn.execute(
                    actives.insert().values(
                        identifier=identifier,
                        owner=owner,
                        owner_id=owner_id,
                        endpoint=endpoint,
                        url=url,
                        switch_date=switch_date
                    )
                )
                await trans.commit()
                await trans.close()
                return json({'message': 'Link created'}, status=201)

            except Exception:
                await trans.close()
                return json({'message': 'Endpoint already exists'}, status=409)

    except Exception:
        await trans.close()
        return json({'message': 'Creating link failed'}, status=500)