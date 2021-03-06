from flask import request, g
from oslo_serialization import jsonutils
from oslo_log import log

from craton.inventory import exceptions
from craton.inventory.api.v1 import base
from craton.inventory import db as dbapi


LOG = log.getLogger(__name__)


class Cells(base.Resource):

    def get(self):
        """Get cell(s) for the project. Get cell details if
        for a particular region.
        """
        region = g.args["region"]
        cell = g.args["name"]
        context = request.environ.get('context')

        if region != 'None' and cell != 'None':
            # Get this particular cell along with its data
            try:
                cell_obj = dbapi.cells_get_by_name(context, region, cell)
            except exceptions.NotFound:
                return self.error_response(404, 'Not Found')
            except Exception as err:
                LOG.error("Error during cells get: %s" % err)
                return self.error_response(500, 'Unknown Error')

            cell_obj.data = cell_obj.variables
            cell = jsonutils.to_primitive(cell_obj)
            return [cell], 200, None

        if region == 'None':
            # Get all cells for all regions
            try:
                cell_obj = dbapi.cells_get_all(context, None)
                cell = jsonutils.to_primitive(cell_obj)
                return cell, 200, None
            except exceptions.NotFound:
                return self.error_response(404, 'Not Found')

        if region != 'None' and cell == 'None':
            # Get all cells for this region only
            try:
                cells_obj = dbapi.cells_get_all(context, region)
                cells = jsonutils.to_primitive(cells_obj)
                return cells
            except exceptions.NotFound:
                return self.error_response(404, 'Not Found')

    def post(self):
        """Create a new cell."""
        context = request.environ.get('context')
        try:
            dbapi.cells_create(context, g.json)
        except Exception as err:
            LOG.error("Error during cell create: %s" % err)
            return self.error_response(500, 'Unknown Error')

        return None, 200, None

    def put(self, id):
        """Update existing cell."""
        return None, 401, None

    def delete(self, id):
        """Delete existing cell."""
        context = request.environ.get('context')
        try:
            dbapi.cells_delete(context, id)
        except exceptions.NotFound:
            return self.error_response(404, 'Not Found')
        except Exception as err:
            LOG.error("Error during cell delete: %s" % err)
            return self.error_response(500, 'Unknown Error')

        return None, 200, None


class CellsData(base.Resource):

    def put(self, id):
        """
        Update existing cell data, or create if it does
        not exist.
        """
        data_keys = request.form.keys()
        data = dict((key, request.form.getlist(key)[0]) for key in data_keys)
        context = request.environ.get('context')
        try:
            dbapi.cells_data_update(context, id, data)
        except exceptions.NotFound:
            return self.error_response(404, 'Not Found')
        except Exception as err:
            LOG.error("Error during cell data update: %s" % err)
            return self.error_response(500, 'Unknown Error')

        return None, 200, None

    def delete(self, id):
        """Delete cell data."""
        # NOTE(sulo): this is not that great. Find a better way to do this.
        # We can pass multiple keys suchs as key1=one key2=two etc. but not
        # the best way to do this.
        data_keys = request.form.keys()
        data = dict((key, request.form.getlist(key)[0]) for key in data_keys)
        context = request.environ.get('context')
        try:
            dbapi.cells_data_delete(context, id, data)
        except exceptions.NotFound:
            return self.error_response(404, 'Not Found')
        except Exception as err:
            LOG.error("Error during cell delete: %s" % err)
            return self.error_response(500, 'Unknown Error')

        return None, 200, None
