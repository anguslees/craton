import mock

from oslo_serialization import jsonutils

from craton.inventory import api, exceptions
from craton.inventory.api import middleware
from craton.inventory.db.sqlalchemy import api as dbapi
from craton.inventory.tests import TestCase
from craton.inventory.tests.unit import fake_resources


class APIV1Test(TestCase):
    def setUp(self):
        super(APIV1Test, self).setUp()

        # Create the app first
        self.app = api.setup_app()
        # Put the context middleware
        self.app.wsgi_app = middleware.NoAuthContextMiddleware(
            self.app.wsgi_app)
        # Create client
        self.client = self.app.test_client()

    def get(self, path, **kw):
        resp = self.client.get(path=path)
        resp.json = jsonutils.loads(resp.data.decode('utf-8'))
        return resp

    def post(self, path, data, **kw):
        content = jsonutils.dumps(data)
        content_type = 'application/json'
        resp = self.client.post(path=path, content_type=content_type,
                                data=content)
        resp.json = jsonutils.loads(resp.data.decode('utf-8'))
        return resp

    def delete(self, path):
        resp = self.client.delete(path=path)
        return resp


class APIV1CellsTest(APIV1Test):
    @mock.patch.object(dbapi, 'cells_get_all')
    def test_get_cells(self, mock_cells):
        mock_cells.return_value = fake_resources.CELL_LIST
        resp = self.get('v1/cells')
        self.assertEqual(len(resp.json), len(fake_resources.CELL_LIST))

    @mock.patch.object(dbapi, 'cells_get_by_name')
    def test_get_cells_with_name(self, mock_cells):
        mock_cells.return_value = fake_resources.CELL1
        resp = self.get('v1/cells?region=1&name=1')
        self.assertEqual(len(resp.json), 1)
        # Ensure we got the right cell
        self.assertEqual(resp.json[0]["name"], fake_resources.CELL1.name)

    @mock.patch.object(dbapi, 'cells_get_by_name')
    def test_get_cell_no_exist_by_name_fails(self, mock_cell):
        err = exceptions.NotFound()
        mock_cell.side_effect = err
        resp = self.get('v1/cells?region=1&name=dontexist')
        self.assertEqual(404, resp.status_code)

    @mock.patch.object(dbapi, 'cells_create')
    def test_create_cell_with_valid_data(self, mock_cell):
        mock_cell.return_value = None
        data = {'name': 'cell1', 'region_id': 1, 'project_id': "1"}
        resp = self.post('v1/cells', data=data)
        self.assertEqual(200, resp.status_code)

    @mock.patch.object(dbapi, 'cells_create')
    def test_create_cell_fails_with_invalid_data(self, mock_cell):
        mock_cell.return_value = None
        # data is missing required cell name
        data = {'region_id': 1, 'project_id': "1"}
        resp = self.post('v1/cells', data=data)
        self.assertEqual(422, resp.status_code)

    @mock.patch.object(dbapi, 'cells_delete')
    def test_cells_delete(self, mock_cell):
        resp = self.delete('v1/cells/1')
        self.assertEqual(200, resp.status_code)


class APIV1RegionsTest(APIV1Test):

    @mock.patch.object(dbapi, 'regions_get_all')
    def test_regions_get_all(self, mock_regions):
        mock_regions.return_value = fake_resources.REGIONS_LIST
        resp = self.get('v1/regions')
        self.assertEqual(len(resp.json), len(fake_resources.REGIONS_LIST))

    def test_regions_get_by_id(self):
        pass

    def test_get_region_by_name(self):
        pass

    def test_get_region_no_exist_by_name_fails(self):
        pass

    def test_post_region_with_valid_data(self):
        pass

    def test_post_region_with_invalid_data_fails(self):
        pass

    def test_delete_region_no_exist_fails(self):
        pass


class APIV1HostsTest(TestCase):
    def test_get_hosts(self):
        pass

    def test_get_host_by_name(self):
        pass

    def test_get_host_by_ip_address(self):
        pass

    def test_get_host_by_filter_query(self):
        pass

    def test_get_host_no_exist_fails(self):
        pass
