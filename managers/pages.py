from config import HTML
from config import INFO, MODEL
from config import GITHUB, SUPABASE, QDRANT


class Pages(object):
	def __init__(self):
		return

	def root (self):
		html = HTML
		html += f"<h3>{INFO}</h3>"
		html += f"<h3>{MODEL}</h3>"
		html += """
		        <table class="my-table">
		            <tr>
		                <td class="col-30">Supabase URL</td>
		                <td class="col-60">Qdrant URL</td>
		                <td class="col-30">GitHub Repository URL</td>
		            </tr>
		"""
		html += f"<tr><td class='col-30'><a href=\"{SUPABASE}\">{SUPABASE}</a></td><td class='col-60'><a href=\"{QDRANT}\">{QDRANT}</a></td><td class='col-30'><a href=\"{GITHUB}\">{GITHUB}</a></td></tr>"
		html += "</table>"
		html += """
		        <br>
		        <table class="my-table_2">
		            <tr>
		                <td class="col-20">API</td>
		            </tr>
		"""
		html += f"<tr><td class='col-30'><a href=\"/api/v5/reload\">/api/v5/reload</a></td></tr>"
		html += f"<tr><td class='col-30'><a href=\"/api/v5/search/verify\">/api/v5/search/verify</a></td></tr>"
		html += f"<tr><td class='col-30'><a href=\"/api/v6/search/verify\">/api/v6/search/verify</a></td></tr>"

		html += """
		            </table>
		    """
		html += """
		        <br>
		        <table class="my-table_2">
		            <tr>
		                <td class="col-30">Call #1</td>
		                <td class="col-30">Call #2</td>
		            </tr>

		            <tr>
		                <td class="col-30">
		                    <img src="/docs/call_1.jpg" alt="Call #1" style="width:450px;height:470px;"/>
		                </td>
		                <td class="col-30">
		                    <img src="/docs/call_2.jpg" alt="Call #2" style="width:450px;height:470px;"/>
		                </td>
		            </tr>
		        </table>
		"""
		html += """
		        </body>
		"""
		return html;