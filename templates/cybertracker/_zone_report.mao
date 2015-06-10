<%
  zones = zone_summary.keys()
  if zones[0] == 'Other zone':
    x = zones.pop(0)
    zones.append(x)
%>

% if not data:

<p>
  No observations were found for this report.
</p>

% else:

<p>
  Number of observations: ${summary['number_records']}
  <br />
  Observations recorded: ${summary['start'].strftime("%m/%d/%y %I:%M%p")} through ${summary['end'].strftime("%m/%d/%y %I:%M%p")}
</p>

% if sort_by and sort_by != 'weight':
<p>
  Sorting by: ${'Total' if sort_by == 'total_tally' else sort_by}
</p>
% endif

<table style="width:100%; padding: 4px; cell-spacing: 4px" border="0">
  <tr>
    <td colspan="2">&nbsp;</td>
    % for zone in zones:
    <td rowspan="2" valign="top" nowrap="nowrap">
      <strong><a href="${base_path}/cybertracker/zone_report/${group_code}/?sort_by=${zone}">${zone}</a></strong>
    </td>
    % endfor
    <td>&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td nowrap="nowrap">
      <strong><a href="${base_path}/cybertracker/zone_report/${group_code}/">Name</a></strong>
    </td>
    <td rowspan="1" align="center">
      <strong>Habitat</strong>
    </td>
    <td rowspan="1" align="center" bgcolor="#AAAAAA">
      <strong><a href="${base_path}/cybertracker/zone_report/${group_code}/?sort_by=total_tally">Total</a></strong>
    </td>
  </tr>
  % for index, datum in enumerate(data):
  <tr bgcolor="${'#dddddd' if index % 2 == 0 else '#ffffff'}">
    <td valign="middle" align="right" bgcolor="#ffffff">
      <img src="${base_path}${datum['animal_group_icon']}" alt="${datum['animal_group']}" />
    </td>
    <td valign="middle">
      <strong>${datum['animal']}</strong>
    </td>
    % for zone in zones:
      <td valign="middle" align="center">
        ${datum[zone] if zone in datum else '0'}
      </td>
    % endfor
    <td valign="middle" align="left" style="font-size: 9pt">
      % if datum['where_observed']:
      <small>
      ${'- ' + '<br />- '.join(datum['where_observed'])}
      </small>
      % endif
    </td>
    <td valign="middle" align="center" bgcolor="#AAAAAA">
      <strong>${datum['total_tally']}</strong>
    </td>
  </tr>
  % endfor
  <tr>
    <td colspan="${4 + len(zones)}" style="border-top: 2px solid black">&nbsp;</td>
  </tr>
  <tr>
    <td colspan="2">
      <strong>Number of Animals (Abundance)</strong>
    </td>
    % for zone in zones:
    <td valign="middle" align="center">
      <strong>${zone_summary[zone]['total_animals']}</strong>
    </td>
    % endfor
    <td>&nbsp;</td>
    <td valign="middle" align="center" bgcolor="#AAAAAA">
      <strong>${summary['total_animals']}</strong>
    </td>
  </tr>
  <tr>
    <td colspan="2"><strong>Number of Kinds of Animals (Richness)</strong></td>
    % for zone in zones:
    <td valign="middle" align="center">
      <strong>${zone_summary[zone]['distinct_animals']}</strong>
    </td>
    % endfor
    <td>&nbsp;</td>
    <td valign="middle" align="center" bgcolor="#AAAAAA">
      <strong>${summary['distinct_animals']}</strong>
    </td>
  </tr>
</table>

% endif
