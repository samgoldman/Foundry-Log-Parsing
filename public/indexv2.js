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
        if (
          data["field_metadata"][c] !== undefined &&
          data["field_metadata"][c]["is_percent"] === true
        ) {
          row.appendChild(
            createCell("th", formatter.format(data[user][c] * 100) + "%")
          );
        } else {
          row.appendChild(createCell("th", data[user][c]));
        }
      });

      body.append(row);
    });
    table.append(body);
  });

  document.querySelectorAll(".bar_chart").forEach((chartDiv) => {
    let chart_data = [];
    let fields = chartDiv.dataset.field.split(" ");
    let colors = undefined;
    if (chartDiv.dataset.colors !== undefined) {
      colors = chartDiv.dataset.colors.split(" ");
    }

    let min = 999999999;
    let max = 0;

    let i = 0;
    fields.forEach((field) => {
      let bar_data = [];
      let bar_text = [];
      let field_base = field.split("_").slice(0, -1).join("_")
      users.forEach((user) => {
        bar_data.push(data[user][field]);
        bar_text.push(`n=${data[user][`${field_base}_count`]}`);
      });

      min = d3.max([0, d3.min([d3.min(bar_data), min])]);
      max = d3.max([d3.max(bar_data), max]);

      if (chartDiv.dataset.zeroIsZero !== undefined) {
        min = 0;
      }

      let marker = {};
      if (colors !== undefined) {
        marker = {
          color: colors[i]
        }
      }

      chart_data.push({
        x: users,
        y: bar_data,
        type: "bar",
        marker: marker,
        text: bar_text,
        name: data["field_metadata"][field]["pretty"],
      });
      i += 1;
    });

    min -= min*.1;
    max += max*.1;

    let title = chartDiv.dataset.title;

    if (title === undefined) {
      if (data["field_metadata"][fields[0]] !== undefined) {
        title = data["field_metadata"][fields[0]]["pretty"];
      }
    }

    let ytick_format = "";
    if (data["field_metadata"][fields[0]]["is_percent"]) {
      ytick_format = ".0%";
    }

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
        tickformat: ytick_format,
        range: [min, max],
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
