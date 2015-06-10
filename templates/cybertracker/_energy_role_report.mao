% if not data:

<p>
  No observations were found for this report.
</p>

% else:

<p>
  Number of observations: ${summary['number_records']}
  % if skipped > 0:
    (${skipped} skipped)
  % endif
  <br />
  Observations recorded: ${summary['start'].strftime("%m/%d/%y %I:%M%p")} through ${summary['end'].strftime("%m/%d/%y %I:%M%p")}
</p>

<table cellspacing="0" cellpadding="6" border="0" width="100%" class="report">
  <tr>
    <th class="${'sorted' if sort_by == 'group' else '' }">
      <a href="${base_path}/cybertracker/energy_role_report/${group_code}/?sort_by=group">Group</a>
    </th>
    <th class="${'sorted' if sort_by == 'observed' else '' }">
      <a href="${base_path}/cybertracker/energy_role_report/${group_code}/?sort_by=observed">Observed</a>
    </th>
    <th class="${'sorted' if sort_by == 'energy_role' else '' }">
      <a href="${base_path}/cybertracker/energy_role_report/${group_code}/?sort_by=energy_role">Energy Role</a>
    </th>
    <th class="${'sorted' if sort_by == 'total_tally' else '' }">
      <a href="${base_path}/cybertracker/energy_role_report/${group_code}/?sort_by=total_tally">How Many?</a>
    </th>
    <th class="r">
      If some were seen eating, what where they eating?
    </th>
  </tr>
  % for index, datum in enumerate(data):
    <% b = 'b' if datum == data[-1] else '' %>
  <tr class="${'even' if index % 2 == 0 else 'odd'}">
    <td class="c ${b}">
      % if datum['group'] == 'Plant':
        Plant
      % else:
      <img src="${base_path}${datum['group_icon']}" alt="${datum['group']}" />
      % endif
    </td>
    <td class="l ${b}">
      ${datum['observed']}
    </td>
    <td class="c ${b}">
      ${datum['energy_role']}
    </td>
    <td class="c ${b}">
      % if datum['how_much_grass']:
      ${datum['how_much_grass']}
      % else:
      ${datum['total_tally']}
      % endif
    </td>
    <td class="r ${b}">
      % if datum['what_eating']:
      <small>
      ${'- ' + '<br />- '.join(datum['what_eating'])}
      </small>
      % else:
      &nbsp;
      % endif
    </td>
  </tr>
  % endfor
  <tr>
    <td class="t c">Total</td>
    <td class="t">&nbsp;</td>
    <td class="t">&nbsp;</td>
    <td class="t c">${total}</td>
    <td class="t">&nbsp;</td>
  </tr>
</table>

% endif
