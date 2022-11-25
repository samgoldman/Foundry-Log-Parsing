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

function tabulate(
  id,
  data,
  columns,
  column_name_map,
  column_pct_map,
  column_roll_fmt_map
) {
  const table = d3.select(id);
  const thead = table.append("thead");
  const tbody = table.append("tbody");

  // append the header row
  thead
    .append("tr")
    .selectAll("th")
    .data(columns)
    .enter()
    .append("th")
    .text(function (column) {
      if (column_name_map[column] === undefined) {
        return column;
      } else {
        return column_name_map[column];
      }
    });

  // create a row for each object in the data
  const rows = tbody.selectAll("tr").data(data).enter().append("tr");
  const formatter = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  // create a cell in each row for each column
  const cells = rows
    .selectAll("td")
    .data(function (row) {
      return columns.map(function (column) {
        if (
          column_pct_map[column] !== undefined &&
          column_pct_map[column] === true
        ) {
          return {
            column: column,
            value: formatter.format(row[column] * 100) + "%",
          };
        } else if (
          column_roll_fmt_map[column] !== undefined &&
          column_roll_fmt_map[column] === true
        ) {
          return { column: column, value: formatter.format(row[column]) };
        } else {
          return { column: column, value: row[column] };
        }
      });
    })
    .enter()
    .append("td")
    .text(function (d) {
      return d.value;
    });

  return table;
}

let world = "salocaia";
if (window.location.hash) {
  world = window.location.hash.slice(1);
}

d3.queue()
  .defer(d3.json, `${world}_data.json`)
  .await((error, d20_data) => {
    const column_name_map = {
      player: "Player",
      roll_count: "D20 Rolls",
      roll_count_prev: "D20s Last Session",
      advantage_count: "Rolls with Advantage",
      disadvantage_count: "Rolls with Disadvantage",
      advantage_ratio: "% Advantage",
      disadvantage_ratio: "% Disadvantage",
      attack_roll_count: "Attacks",
      attack_roll_count_prev: "Attacks Last Session",
      attack_roll_ratio: "% Attacks",
      saving_throw_count: "Saves",
      saving_throw_count_prev: "Saves Last Session",
      saving_throw_ratio: "% Saves",
      ability_check_count: "Ability Checks",
      ability_check_count_prev: "Ability Checks Last Session",
      ability_check_ratio: "% Ability Checks",
      skill_check_count: "Skill Checks",
      skill_check_count_prev: "Skill Checks Last Session",
      skill_check_ratio: "% Skill Checks",
      initiative_roll_count: "Initiative Rolls",
      initiative_roll_count_prev: "Initiative Rolls Last Session",
      initiative_roll_ratio: "% Initiative Rolls",
      nat_20_count: "Nat 20s",
      nat_20_count_prev: "Nat 20s Last Session",
      nat_20_ratio: "% Nat 20s",
      nat_1_count: "Nat 1s",
      nat_1_count_prev: "Nat 1s Last Session",
      nat_1_ratio: "% Nat 1s",
      stolen_nat_20_count: "Stolen Nat 20s",
      super_nat_20_count: "Super Nat 20s",
      disadvantage_nat_20_count: "Disadvantage Nat 20s",
      dropped_nat_1_count: "Dropped Nat 1s",
      super_nat_1_count: "Super Nat 1s",
      advantage_nat_1_count: "Advantage Nat 1s",
      stolen_nat_20_count_prev: "Stolen Nat 20s Last Session",
      super_nat_20_count_prev: "Super Nat 20s Last Session",
      disadvantage_nat_20_count_prev: "Disadvantage Nat 20s Last Session",
      dropped_nat_1_count_prev: "Dropped Nat 1s Last Session",
      super_nat_1_count_prev: "Super Nat 1s Last Session",
      advantage_nat_1_count_prev: "Advantage Nat 1s Last Session",
      average_raw_d20_roll: "Raw D20 (inc. dropped)",
      average_final_d20_roll: "Raw D20 (after adv./disadv.)",
      average_d20_after_modifiers: "D20 after Mods",
      average_attack_before_modifiers: "Attacks before Mods",
      average_initiative_before_modifiers: "Initiative before Mods",
      average_save_before_modifiers: "Saves before Mods",
      average_skill_before_modifiers: "Skill Checks before Mods",
      average_ability_before_modifiers: "Ability Checks before Mods",
      average_attack_after_modifiers: "Attacks after Mods",
      average_initiative_after_modifiers: "Initiative after Mods",
      average_save_after_modifiers: "Saves after Mods",
      average_skill_after_modifiers: "Skill Checks after Mods",
      average_ability_after_modifiers: "Ability Checks after Mods",
    };
    const column_pct_map = {
      advantage_ratio: true,
      disadvantage_ratio: true,
      attack_roll_ratio: true,
      initiative_roll_ratio: true,
      saving_throw_ratio: true,
      ability_check_ratio: true,
      skill_check_ratio: true,
      nat_20_ratio: true,
      nat_1_ratio: true,
    };
    const column_roll_fmt_map = {
      average_raw_d20_roll: true,
      average_final_d20_roll: true,
      average_d20_after_modifiers: true,
      average_attack_before_modifiers: true,
      average_initiative_before_modifiers: true,
      average_save_before_modifiers: true,
      average_skill_before_modifiers: true,
      average_ability_before_modifiers: true,
      average_attack_after_modifiers: true,
      average_initiative_after_modifiers: true,
      average_save_after_modifiers: true,
      average_skill_after_modifiers: true,
      average_ability_after_modifiers: true,
    };

  tabulate(
    "#advantage",
    d20_data,
    [
      "player",
      "roll_count",
      "advantage_count",
      "advantage_ratio",
      "disadvantage_count",
      "disadvantage_ratio",
    ],
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
  );
  tabulate(
    "#type_of_roll",
    d20_data,
    [
      "player",
      "roll_count",
      "roll_count_prev",
      "attack_roll_count",
      "attack_roll_count_prev",
      "saving_throw_count",
      "saving_throw_count_prev",
      "ability_check_count",
      "ability_check_count_prev",
      "skill_check_count",
      "skill_check_count_prev",
      "initiative_roll_count",
      "initiative_roll_count_prev",
    ],
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
  );

  tabulate(
    "#type_of_roll_pct",
    d20_data,
    [
      "player",
      "roll_count",
      "attack_roll_ratio",
      "saving_throw_ratio",
      "ability_check_ratio",
      "skill_check_ratio",
      "initiative_roll_ratio",
    ],
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
  );
  tabulate(
    "#crits",
    d20_data,
    [
      "player",
      "roll_count",
      "nat_20_count",
      "nat_20_count_prev",
      "nat_20_ratio",
      "nat_1_count",
      "nat_1_count_prev",
      "nat_1_ratio",
      "stolen_nat_20_count",
      "stolen_nat_20_count_prev",
      "super_nat_20_count",
      "super_nat_20_count_prev",
      "disadvantage_nat_20_count",
      "disadvantage_nat_20_count_prev",
      "dropped_nat_1_count",
      "dropped_nat_1_count_prev",
      "super_nat_1_count",
      "super_nat_1_count_prev",
      "advantage_nat_1_count",
      "advantage_nat_1_count_prev",
    ],
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
  );
  tabulate(
    "#d20_performance_by_type",
    d20_data,
    [
      "player",
      "roll_count",
      "average_raw_d20_roll",
      "average_final_d20_roll",
      "average_d20_after_modifiers",
      "average_attack_before_modifiers",
      "average_attack_after_modifiers",
      "average_save_before_modifiers",
      "average_save_after_modifiers",
      "average_skill_before_modifiers",
      "average_skill_after_modifiers",
      "average_ability_before_modifiers",
      "average_ability_after_modifiers",
      "average_initiative_before_modifiers",
      "average_initiative_after_modifiers",
    ],
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
  );
  const SKILLS = {
    acr: "Acrobatics",
    ani: "Animal Handling",
    arc: "Arcana",
    ath: "Athletics",
    dec: "Deception",
    his: "History",
    ins: "Insight",
    itm: "Intimidation",
    inv: "Investigation",
    med: "Medicine",
    nat: "Nature",
    prc: "Perception",
    prf: "Performance",
    per: "Persuasion",
    rel: "Religion",
    slt: "Sleight of Hand",
    ste: "Stealth",
    sur: "Survival",
  };
  const ABILITIES = {
    str: "Strength",
    dex: "Dexterity",
    con: "Constitution",
    int: "Intelligence",
    wis: "Wisdom",
    cha: "Charisma",
  };
  const SAVES = { death: "Death", ...ABILITIES };

  let specific_save_columns = ["player", "saving_throw_count"];
  let specific_ability_columns = ["player", "ability_check_count"];
  let skill_count_columns = ["player", "skill_check_count"];
  let skill_average_columns = ["player", "skill_check_count"];
  for (const [key, value] of Object.entries(SKILLS)) {
    skill_count_columns.push(`${key}_skill_count`);
    skill_average_columns.push(`${key}_skill_average`);
    column_name_map[`${key}_skill_count`] = `${value} Count`;
    column_name_map[`${key}_skill_average`] = `Avg. ${value}`;
    column_roll_fmt_map[`${key}_skill_average`] = true;
  }
  for (const [key, value] of Object.entries(ABILITIES)) {
    specific_ability_columns.push(`${key}_ability_count`);
    specific_ability_columns.push(`${key}_ability_average`);
    column_name_map[`${key}_ability_count`] = `${value} Count`;
    column_name_map[`${key}_ability_average`] = `Avg. ${value}`;
    column_roll_fmt_map[`${key}_ability_average`] = true;
  }
  for (const [key, value] of Object.entries(SAVES)) {
    specific_save_columns.push(`${key}_save_count`);
    specific_save_columns.push(`${key}_save_average`);
    column_name_map[`${key}_save_count`] = `${value} Count`;
    column_name_map[`${key}_save_average`] = `Avg. ${value}`;
    column_roll_fmt_map[`${key}_save_average`] = true;
  }

  tabulate(
    "#save_specific_data",
    d20_data,
    specific_save_columns,
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
  );
  tabulate(
    "#ability_specific_data",
    d20_data,
    specific_ability_columns,
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
  );
  tabulate(
    "#skill_specific_data1",
    d20_data,
    skill_count_columns,
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
  );
  tabulate(
    "#skill_specific_data2",
    d20_data,
    skill_average_columns,
    column_name_map,
    column_pct_map,
    column_roll_fmt_map
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
