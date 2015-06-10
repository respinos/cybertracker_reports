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
    <th class="${'sorted' if sort_by == 'where_observed' else '' }">
      <a href="${base_path}/cybertracker/habitat_report/${group_code}/?sort_by=where_observed">Habitat</a>
    </th>
    <th class="${'sorted' if sort_by == 'animal_group' else '' }">
      <a href="${base_path}/cybertracker/habitat_report/${group_code}/?sort_by=animal_group">Animal Group</a>
    </th>
    <th class="${'sorted' if sort_by == 'animal' else '' }">
      <a href="${base_path}/cybertracker/habitat_report/${group_code}/?sort_by=animal">Animal</a>
    </th>
    <th class="${'sorted' if sort_by == 'total_tally' else '' }">
      <a href="${base_path}/cybertracker/habitat_report/${group_code}/?sort_by=total_tally">How Many?</a>
    </th>
    <th class="r">
      Location
    </th>
  </tr>
  % for index, datum in enumerate(data):
    <% b = 'b' if datum == data[-1] else '' %>
  <tr class="${'even' if index % 2 == 0 else 'odd'}">
    <td class="c ${b}">
      ${datum['where_observed']}
    </td>
    <td class="c ${b}">
      <img src="${base_path}${datum['animal_group_icon']}" alt="${datum['animal_group']}" />
    </td>
    <td class="l ${b}">
      ${datum['animal']}
    </td>
    <td class="c ${b}">
      ${datum['total_tally']}
    </td>
    <td class="r ${b}">
      % if datum['location']:
      <small>
      ${'- ' + '<br />- '.join(datum['location'])}
      </small>
      % endif
    </td>
  </tr>
  % endfor
</table>

% endif
