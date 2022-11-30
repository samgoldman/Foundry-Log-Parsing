let world = "salocaia";
if (window.location.hash !== undefined && window.location.hash.length > 1) {
  world = window.location.hash.slice(1);
}

const formatter = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

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
        if (data["field_metadata"][c] !== undefined && data["field_metadata"][c]["is_percent"] === true) {
          row.appendChild(createCell("th", formatter.format(data[user][c] * 100) + "%"))
        } else {
          row.appendChild(createCell("th", data[user][c]));
        }
      });

      body.append(row);
    });
    table.append(body);
  });

  document.querySelectorAll(".bar_chart").forEach((chartDiv) => {
    let field_base = chartDiv.dataset.field;

    let bar_data = [];
    let bar_text = [];
    users.forEach((user) => {
      bar_data.push(data[user][`${field_base}_average`]);
      bar_text.push(`n=${data[user][`${field_base}_count`]}`);
    });

    let title = `${field_base}_average`;
    if (data["field_metadata"][`${field_base}_average`] !== undefined) {
      title = data["field_metadata"][`${field_base}_average`]["pretty"];
    }

    let chart_data = [
      {
        x: users,
        y: bar_data,
        type: "bar",
        text: bar_text,
      },
    ];
    let layout = {
      title: {
        text: title,
        y: 1,
        yref: "paper",
        font: {
          size: 30,
        },
      },
      width: 960,
      font: {
        family: "Courier New, monospace",
        size: 16,
        color: "#000",
      },
      yaxis: {
        tickfont: {
          size: 24,
        },
        range: [d3.max([0, d3.min(bar_data) - 1]), d3.max(bar_data) + 1],
      },
    };
    let config = {
      responsive: true,
    };
    // Populate graphs
    Plotly.newPlot(chartDiv, chart_data, layout, config);
  });

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
