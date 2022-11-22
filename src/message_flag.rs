use serde::Deserialize;

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(tag = "abilityId")]
#[serde(deny_unknown_fields)]
pub enum SaveType {
    #[serde(rename = "str")]
    Strength,
    #[serde(rename = "dex")]
    Dexterity,
    #[serde(rename = "con")]
    Constitution,
    #[serde(rename = "int")]
    Intelligence,
    #[serde(rename = "wis")]
    Wisdom,
    #[serde(rename = "cha")]
    Charisma,
    #[serde(rename = "death")]
    Death,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(tag = "abilityId")]
#[serde(deny_unknown_fields)]
pub enum Ability {
    #[serde(rename = "str")]
    Strength,
    #[serde(rename = "dex")]
    Dexterity,
    #[serde(rename = "con")]
    Constitution,
    #[serde(rename = "int")]
    Intelligence,
    #[serde(rename = "wis")]
    Wisdom,
    #[serde(rename = "cha")]
    Charisma,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(tag = "skillId")]
#[serde(deny_unknown_fields)]
pub enum Skill {
    #[serde(rename = "ani")]
    AnimalHandling,
    #[serde(rename = "acr")]
    Acrobatics,
    #[serde(rename = "arc")]
    Arcana,
    #[serde(rename = "ath")]
    Athletics,
    #[serde(rename = "dec")]
    Deception,
    #[serde(rename = "his")]
    History,
    #[serde(rename = "ins")]
    Insight,
    #[serde(rename = "itm")]
    Intimidation,
    #[serde(rename = "inv")]
    Investigation,
    #[serde(rename = "med")]
    Medicine,
    #[serde(rename = "nat")]
    Nature,
    #[serde(rename = "prf")]
    Performance,
    #[serde(rename = "prc")]
    Perception,
    #[serde(rename = "per")]
    Persuasion,
    #[serde(rename = "rel")]
    Religion,
    #[serde(rename = "slt")]
    SleightOfHand,
    #[serde(rename = "ste")]
    Stealth,
    #[serde(rename = "sur")]
    Survival,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ItemId {
    #[serde(rename = "itemId")]
    pub id: String,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(tag = "type")]
#[serde(deny_unknown_fields)]
pub enum RollType {
    #[serde(rename = "save")]
    SavingThrow(SaveType),
    #[serde(rename = "ability")]
    AbilityCheck(Ability),
    #[serde(rename = "skill")]
    SkillCheck(Skill),
    #[serde(rename = "attack")]
    Attack(ItemId),
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
#[serde(deny_unknown_fields)]
pub enum Dnd5eFlag {
    Roll(RollType),
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CoreFlag {
    #[serde(rename = "canPopout")]
    pub can_popout: bool,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
#[serde(deny_unknown_fields)]
pub enum MessageFlag {
    DnD5E(Dnd5eFlag),
    Core(CoreFlag),
}

#[cfg(test)]
mod tests {
    use super::*;

    macro_rules! test_deserialize_saving_throw {
        ($fn:ident, $short:literal, $expected:expr) => {
            #[test]
            fn $fn() {
                let json = format!(
                    r#"{{"dnd5e":{{"roll":{{"type":"save","abilityId":"{}"}}}}}}"#,
                    $short
                );

                assert_eq!(
                    MessageFlag::DnD5E(Dnd5eFlag::Roll(RollType::SavingThrow($expected))),
                    serde_json::from_str(&json).unwrap()
                );
            }
        };
    }

    test_deserialize_saving_throw!(deserialize_str_saving_throw, "str", SaveType::Strength);
    test_deserialize_saving_throw!(deserialize_dex_saving_throw, "dex", SaveType::Dexterity);
    test_deserialize_saving_throw!(deserialize_con_saving_throw, "con", SaveType::Constitution);
    test_deserialize_saving_throw!(deserialize_int_saving_throw, "int", SaveType::Intelligence);
    test_deserialize_saving_throw!(deserialize_wis_saving_throw, "wis", SaveType::Wisdom);
    test_deserialize_saving_throw!(deserialize_cha_saving_throw, "cha", SaveType::Charisma);
    test_deserialize_saving_throw!(deserialize_death_saving_throw, "death", SaveType::Death);

    macro_rules! test_deserialize_ability_check {
        ($fn:ident, $short:literal, $expected:expr) => {
            #[test]
            fn $fn() {
                let json = format!(
                    r#"{{"dnd5e":{{"roll":{{"type":"ability","abilityId":"{}"}}}}}}"#,
                    $short
                );

                assert_eq!(
                    MessageFlag::DnD5E(Dnd5eFlag::Roll(RollType::AbilityCheck($expected))),
                    serde_json::from_str(&json).unwrap()
                );
            }
        };
    }

    test_deserialize_ability_check!(deserialize_str_ability_check, "str", Ability::Strength);
    test_deserialize_ability_check!(deserialize_dex_ability_check, "dex", Ability::Dexterity);
    test_deserialize_ability_check!(deserialize_con_ability_check, "con", Ability::Constitution);
    test_deserialize_ability_check!(deserialize_int_ability_check, "int", Ability::Intelligence);
    test_deserialize_ability_check!(deserialize_wis_ability_check, "wis", Ability::Wisdom);
    test_deserialize_ability_check!(deserialize_cha_ability_check, "cha", Ability::Charisma);

    macro_rules! test_deserialize_skill_check {
        ($fn:ident, $short:literal, $expected:expr) => {
            #[test]
            fn $fn() {
                let json = format!(
                    r#"{{"dnd5e":{{"roll":{{"type":"skill","skillId":"{}"}}}}}}"#,
                    $short
                );

                assert_eq!(
                    MessageFlag::DnD5E(Dnd5eFlag::Roll(RollType::SkillCheck($expected))),
                    serde_json::from_str(&json).unwrap()
                );
            }
        };
    }

    test_deserialize_skill_check!(deserialize_acr_skill_check, "acr", Skill::Acrobatics);
    test_deserialize_skill_check!(deserialize_ani_skill_check, "ani", Skill::AnimalHandling);
    test_deserialize_skill_check!(deserialize_arc_skill_check, "arc", Skill::Arcana);
    test_deserialize_skill_check!(deserialize_ath_skill_check, "ath", Skill::Athletics);
    test_deserialize_skill_check!(deserialize_dec_skill_check, "dec", Skill::Deception);
    test_deserialize_skill_check!(deserialize_his_skill_check, "his", Skill::History);
    test_deserialize_skill_check!(deserialize_ins_skill_check, "ins", Skill::Insight);
    test_deserialize_skill_check!(deserialize_itm_skill_check, "itm", Skill::Intimidation);
    test_deserialize_skill_check!(deserialize_inv_skill_check, "inv", Skill::Investigation);
    test_deserialize_skill_check!(deserialize_med_skill_check, "med", Skill::Medicine);
    test_deserialize_skill_check!(deserialize_nat_skill_check, "nat", Skill::Nature);
    test_deserialize_skill_check!(deserialize_prc_skill_check, "prc", Skill::Perception);
    test_deserialize_skill_check!(deserialize_prf_skill_check, "prf", Skill::Performance);
    test_deserialize_skill_check!(deserialize_per_skill_check, "per", Skill::Persuasion);
    test_deserialize_skill_check!(deserialize_rel_skill_check, "rel", Skill::Religion);
    test_deserialize_skill_check!(deserialize_slt_skill_check, "slt", Skill::SleightOfHand);
    test_deserialize_skill_check!(deserialize_ste_skill_check, "ste", Skill::Stealth);
    test_deserialize_skill_check!(deserialize_sur_skill_check, "sur", Skill::Survival);

    #[test]
    fn test_deserialize_attack_roll() {
        let json = r#"{"dnd5e":{"roll":{"type":"attack","itemId":"T4fz28UcEkAobU5n"}}}"#;

        assert_eq!(
            MessageFlag::DnD5E(Dnd5eFlag::Roll(RollType::Attack(ItemId {
                id: "T4fz28UcEkAobU5n".to_string()
            }))),
            serde_json::from_str(&json).unwrap()
        );
    }

    #[test]
    fn test_deserialize_core_can_popout() {
        let json = r#"{"core":{"canPopout":true}}"#;

        assert_eq!(
            MessageFlag::Core(CoreFlag {
                can_popout: true,
            }),
            serde_json::from_str(&json).unwrap()
        );
    }
}
