<%
headings = [
  ['name', "Tracker Name", True],
  ['datetime', "Date/Time", True],
  ['location', "Location", True],
  ['group', "Group", True],
  ['observed', "Observed", True],
  ['how_many', "How Many", True],
  ['how_exact', "Exact/Estimate", True],
  ['what_observed', "What observed", False],
  ['how_observed', "How observed", False],
  ['where_observed', "Microhabitat", False],
  ['behavior_observed', "Behavior", False]
]

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

<table cellspacing="0" cellpadding="6" border="0" width="100%" class="report">
  <tr>
    % for heading in headings:
      <th class="${'sorted' if heading[0] == sort_by else ''}">
        % if heading[2]:
          <a href="${base_path}/cybertracker/observation_report/${group_code}/?sort_by=${heading[0]}">${heading[1]}</a>
        % else:
          ${heading[1]}
        % endif
      </th>
    % endfor
  </tr>
  % for index, datum in enumerate(data):
  <tr class="${'even' if index % 2 == 0 else 'odd'}">
    <% b = 'b' if datum == data[-1] else '' %>
    % for heading in headings:
      <% 
        key = heading[0]
        klass = 'class_l' if isinstance(datum[key], list) else 'class_c'
      %>
      <td class="${klass} ${b}">
        % if key == 'datetime':
          ${datum['datetime'].strftime("%m/%d/%y - %I:%M%p")}
        % elif key == 'group':
          % if datum['is_animal']:
          <img src="${base_path}${datum['group_icon']}" alt="${datum['group']}" />
          % else:
          ${datum['group']}
          % endif
        % elif isinstance(datum[key], list):
          % if datum[key]:
            ${'- ' + '<br />- '.join(datum[key])}
          % else:
            &nbsp;
          % endif
        % else:
          ${datum[key]}
        % endif
      </td>
    % endfor
  </tr>
  % endfor
</table>

% endif
