import unittest
import requests
import os
import json


class TestNoLogin(unittest.TestCase):
	def setUp(self):
		self.page = 2
		self.per_page = 4
		os.environ['NO_PROXY'] = '127.0.0.1'
		self.req = requests.get("http://127.0.0.1:5000/api/arrangements/all",
			params = {"page": self.page, "per_page": self.per_page})
		self.response = json.loads(self.req.text)

	def test_status(self):
		self.assertEqual(self.req.status_code, 200)

	def test_param_page(self):
		self.assertEqual(self.response["meta"]["page"], self.page)

	def test_param_per_page(self):
		self.assertEqual(self.response["meta"]["per_page"], self.per_page)

	if __name__ == '__main__':
		unittest.main()


class TestLogin(unittest.TestCase):
	def setUp(self):
		os.environ['NO_PROXY'] = '127.0.0.1'

	def test_login_good(self):
		req = requests.post("http://127.0.0.1:5000/api/arrangements/login",
			json = {"username": "marko", "password": "marko123"})
		self.assertEqual(req.status_code, 200)

	def test_login_bad_password(self):
		req = requests.post("http://127.0.0.1:5000/api/arrangements/login",
			json = {"username": "marko", "password": "marko1234"})
		self.assertEqual(req.status_code, 406)

	def test_login_bad_username(self):
		req = requests.post("http://127.0.0.1:5000/api/arrangements/login",
			json = {"username": "mark", "password": "marko123"})
		self.assertEqual(req.status_code, 404)

	if __name__ == '__main__':
		unittest.main()


class TestTourist(unittest.TestCase):
	def setUp(self):
		self.session = requests.session()
		os.environ['NO_PROXY'] = '127.0.0.1'
		req = self.session.post("http://127.0.0.1:5000/api/arrangements/login",
			json = {"username": "marko", "password": "marko123"})

	def test_available_arrangements(self):
		pass
		req = self.session.get("http://127.0.0.1:5000/api/arrangements/user/available")
		self.assertEqual(req.status_code, 200)

	def test_reservations(self):
		pass
		req = self.session.get("http://127.0.0.1:5000/api/arrangements/user/reservations")
		self.assertEqual(req.status_code, 200)

	def test_profile(self):
		pass
		req = self.session.get("http://127.0.0.1:5000/api/arrangements/user/profile")
		self.assertEqual(req.status_code, 200)

	def tearDown(self):
		self.session.get("http://127.0.0.1:5000/api/arrangements/logout")

	if __name__ == '__main__':
		unittest.main()
