% if not report:

<p>
  No observations were found for this report.
</p>

% else:

<p>
  Number of observations: ${summary['number_records']}
  <br />
  Observations recorded: ${summary['start'].strftime("%m/%d/%y %I:%M%p")} through ${summary['end'].strftime("%m/%d/%y %I:%M%p")}
</p>

  % if sort_by and sort_by != 'how_many':
<p>
  Sorting by: ${sort_by}
</p>
  % endif

  % for team in teams:
  
<h3>
  Class: ${group.name}<br />
  Team Name: ${team[1]}<br />
  ${team[0]}
</h3>

<%doc>
<%
import pprint
pprint.pprint(report)
%>
</%doc>

<table class="report team">
  <tr>
    <th colspan="4" style="background-color: black; color: white">
      Animals
    </th>
  </tr>
  <tr>
    <th colspan="2">
      Animal Group
    </th>
    <th class="c">
      How many?
    </th>
    <th>
      If some were seen eating, what were they eating?
    </th>
  </tr>
  % for index, datum in enumerate(report[team]['animals']):
  <tr xbgcolor="${'#dddddd' if index % 2 == 0 else '#ffffff'}">
    <td valign="middle" align="right" bgcolor="#ffffff" width="32">
      <img src="${base_path}${datum['animal_group_icon']}" alt="${datum['animal_group']}" />
    </td>
    <td valign="middle">
      <strong>${datum['animal_group']}</strong>
    </td>
    <td valign="middle" align="center">
      ${datum['quantity']}
    </td>
    <td valign="middle" align="left" class="r">
      % if datum['what_eating']:
      <small>
      ${'- ' + '<br />- '.join(datum['what_eating'])}
      </small>
      % endif
    </td>
  </tr>
  % endfor
  <!-- <tr>
    <td colspan="4" style="border:0; border-top: 2px solid black">&nbsp;</td>
  </tr> -->
  <tr class="totals">
    <td colspan="2">
      <strong>Total Animals</strong>
    </td>
    <td align="middle">
      ${report[team]['total_animals']}
    </td>
    <td>&nbsp;</td>
  </tr>
</table>

% if report[team]['total_plants']:
<table class="report team" style="margin-top: 25px; width: 40%">
  <tr>
    <th colspan="2" style="background-color: black; color: white">
      Plants
    </th>
  </tr>
  <tr>
    <th colspan="1">
      Plant Group
    </th>
    <th class="c">
      How many?
    </th>
  </tr>
  % for index, datum in enumerate(report[team]['plants']):
  <tr xbgcolor="${'#dddddd' if index % 2 == 0 else '#ffffff'}">
    <td valign="middle">
      <strong>${datum['plant_group']}</strong>
    </td>
    <td valign="middle" align="center" class="r">
      % if datum['plant_group'] == 'Grass':
        ${datum['how_much_grass']}
      % else:
        ${datum['quantity']}
      % endif
    </td>
  </tr>
  % endfor
  <tr class="totals">
    <td colspan="1">
      <strong>Total Plants</strong>
    </td>
    <td align="middle">
      ${report[team]['total_plants']}
    </td>
  </tr>
</table>
% endif

  <hr style="page-break-after: always; border: 0; border-bottom: 1px solid #eee" />

  % endfor

% endif
