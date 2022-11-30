let world = "salocaia";
if (window.location.hash !== undefined && window.location.hash.length > 1) {
  world = window.location.hash.slice(1);
}

let world_cap = world.charAt(0).toUpperCase() + world.slice(1);
document.querySelector("#banner").textContent = `${world_cap} Statistics`;

function createCell(type, contents) {
  let cell = document.createElement(type);
  cell.textContent = contents;
  return cell;
}
function createCellWithAbbr(type, contents, title) {
  let cell = document.createElement(type);
  let abbr = document.createElement("abbr");
  abbr.title = title;
  abbr.textContent = contents;
  cell.append(abbr);
  return cell;
}

d3.json(`${world}_data_v2.json`).then((data) => {
    let users = ["All", "All Players", "Gamemaster"].concat(data["players"]);
    for (const [key, value] of Object.entries(data["All"])) {
      // Populate fields that define "all"
      document
        .querySelectorAll(`.all_${key}`)
        .forEach((element) => (element.textContent = value));
    }

    // Populate tables
    document.querySelectorAll(".data_table").forEach((table) => {
      let columns = table.dataset.columns.split(" ");
      let header = document.createElement("thead");
      let header_row = document.createElement("tr");
      header_row.appendChild(createCell("th", "Player"));
      columns.forEach((c) => {
        if (data["field_metadata"][c] !== undefined) {
          if (data["field_metadata"][c]["explanation"] !== undefined) {
            header_row.appendChild(
              createCellWithAbbr(
                "th",
                data["field_metadata"][c]["pretty"],
                data["field_metadata"][c]["explanation"]
              )
            );
          } else {
            header_row.appendChild(
              createCell("th", data["field_metadata"][c]["pretty"])
            );
          }
        } else {
          header_row.appendChild(createCell("th", c));
        }
      });
      header.append(header_row);
      table.append(header);

      let body = document.createElement("tbody");
      users.forEach((user) => {
        let row = document.createElement("tr");
        row.appendChild(createCell("th", user));

        columns.forEach((c) => {
          row.appendChild(createCell("th", data[user][c]));
        });

        body.append(row);
      });
      table.append(body);
    });

    let bar_data = [];
    users.forEach((user) =>
      bar_data.push(data[user]["average_raw_d20_roll"])
    );
    let chart_data = [
      {
        x: users,
        y: bar_data,
        type: 'bar'
      }
    ];
    let layout = {
      title: 'Average Raw d20',
      width: 960,
      yaxis: {
        range: [d3.min(bar_data) - 1, d3.max(bar_data) + 1]
      }
    };
    let config = {
      responsive: true
    };
    // Populate graphs
    Plotly.newPlot('average_raw_d20_bar', chart_data, layout, config);

    const getCellValue = (tr, idx) => {
      let v = tr.children[idx].innerText || tr.children[idx].textContent;
      if (v.slice(-1) === "%") {
        return parseFloat(v.slice(0, -1));
      }
      return v;
    };

    const comparer = (idx, asc) => (a, b) =>
      ((v1, v2) =>
        v1 !== "" && v2 !== "" && !isNaN(v1) && !isNaN(v2)
          ? v1 - v2
          : v1.toString().localeCompare(v2))(
        getCellValue(asc ? a : b, idx),
        getCellValue(asc ? b : a, idx)
      );

    document.querySelectorAll("th").forEach((th) =>
      th.addEventListener("click", () => {
        const table = th.closest("table");
        const tbody = table.querySelector("tbody");
        Array.from(tbody.querySelectorAll("tr"))
          .sort(
            comparer(
              Array.from(th.parentNode.children).indexOf(th),
              (this.asc = !this.asc)
            )
          )
          .forEach((tr) => tbody.appendChild(tr));
      })
    );
  });
