########
## A script containing functions for use in other R scripts
## Author: Yamina Boukari
########

# to use in other scripts, include the following code at the start of each script:
# source(here("analysis", "lib", "utility.R"))

library(gtsummary)
library(dplyr)
library(here)
library(janitor)
library(fs)
library(readr)
library(tools)
library(arrow)
library(here)
library(rlang)

## Function to generate and save a demographics table as a csv

generate_demographics_table <- function(cohort_file, by_category = NULL, output_file) {
  
  by_category <- enquo(by_category) 
  
  if (quo_is_null(by_category)) {
    demographics <- cohort_file %>%
      tbl_summary(
        statistic = list(
          all_categorical() ~ "{n} ({p}%)",
          all_continuous() ~ "{median} ({p25}-{p75})",
          all_dichotomous() ~ "{n} ({p}%)"
        ),
        missing = "ifany"
      ) %>%
      bold_labels()
  } else {
    demographics <- cohort_file %>%
      tbl_summary(
        by = !!by_category,
        statistic = list(
          all_categorical() ~ "{n} ({p}%)",
          all_continuous() ~ "{median} ({p25}-{p75})",
          all_dichotomous() ~ "{n} ({p}%)"
        ),
        missing = "ifany"
      ) %>%
      add_overall() %>%
      bold_labels()
  }
    
  demographics_tibble <- as_tibble(demographics, include = "tibble")
  
  dir_create(path_dir(output_file))
  write_csv(demographics_tibble, path = output_file)
}

# function to redact a table 
# Written by W. Hulme: https://github.com/opensafely/CAP-CES/blob/main/analysis/0-lib/redaction.R

redact_tblsummary <- function(x, threshold, redact_chr=NA_character_){

  ## function to redact a tbl_summary object
  ## x is a tbl_summary object
  ## threshold is the redaction threshold, passed to the redactor2 function
  ## redact_chr is the character string used to replace redacted statistics. default is NA

  ## the function redacts all statistics based on counts less than 5 (including means, medians, etc)
  ## it also removes potentially disclosive items from the object, namely:
  ##  - `x$inputs$data` which contains the input data
  ##  - `x$inputs$meta_data` which contains the raw summary table for the table

  stopifnot("x must be a tbl_summary object" = all(class(x) %in% c("tbl_summary", "gtsummary")))

  raw_stats <- x$meta_data %>%
    select(var_label, df_stats) %>%
    unnest(df_stats) %>%
    mutate(
      redact_n = if_else(is.na(n), N_obs, n),
      variable_levels = if_else(!is.na(variable_levels), as.character(variable_levels), var_label)
    )

  if(x$inputs$missing %in% c("ifany", "always")){
    missing_stats <- raw_stats %>%
      select(by, var_label, variable, N_miss, N_obs, N) %>%
      distinct() %>%
      mutate(
        stat_display = "{N_miss}",
        row_type = "missing",
        redact_n = N_miss,
        variable_levels = x$inputs$missing_text
      ) %>%
      filter(N_miss>0 & x$inputs$missing!="always")

    raw_stats <- bind_rows(raw_stats, missing_stats)
  }

  name_by_stat <- set_names(x$df_by$by_col, as.character(x$df_by$by))
  name_stat_by <- set_names(as.character(x$df_by$by), x$df_by$by_col)

  table_body_long <- x$table_body %>%
    pivot_longer(cols=starts_with("stat_"), names_to="by", values_to="display") %>%
    mutate(
      by = fct_recode(by, .fun=!!!name_by_stat)
    )

  redacted_stats <-
    left_join(
      raw_stats %>%
        select(by, var_label, variable, variable_levels, redact_n),
      table_body_long %>%
        filter(!is.na(display)),
      by=c("by", "var_label", "variable", "variable_levels"="label")
    ) %>%
    group_by(by, var_label) %>%
    mutate(
      display=redactor2(redact_n, threshold, display),
      display = if_else(is.na(display), redact_chr, display)
    )

  redacted_body <-
    left_join(
      table_body_long %>% select(-display),
      redacted_stats %>% select(by, variable, var_label, variable_levels, display),
      by=c("by", "variable", "var_label", "label"="variable_levels")
    ) %>%
    mutate(
      by = fct_recode(by, .fun=!!!name_stat_by)
    ) %>%
    pivot_wider(
      id_cols = c(variable, var_type, var_class, var_label, row_type, label), # removed var_class
      names_from = by,
      values_from = display
    )

  x$table_body <- redacted_body

  x$inputs$data <- NULL
  x$inputs$meta_data <- NULL
  x$inputs$label <- NULL

  x

}

## Create table1-style summary of characteristics, with SDC applied ----
# Written by W. Hulme: https://github.com/opensafely/CAP-CES/blob/main/analysis/0-lib/utility.R

table1_summary <- function(.data, group, label, threshold) {
  
  ## this function is highly dependent on the structure of tbl_summary object internals!
  ## be careful if this package is updated
  
  group_quo <- enquo(group)
  
  ## create a table of baseline characteristics between each treatment group, before matching / weighting
  tab_summary <-
    .data |>
    select(
      !!group_quo,
      any_of(names(label)),
    ) %>%
    gtsummary::tbl_summary(
      by = !!group_quo,
      label = label[names(label) %in% names(.)],
      statistic = list(
        N ~ "{N}",
        all_categorical() ~ "{n} ({p}%)",
        all_continuous() ~ "{mean} ({sd}); ({p10}, {p25}, {median}, {p75}, {p90})"
      ),
    )

  ## extract structured info from tbl_summary object to apply SDC to the counts 
  raw_stats <- 
    tab_summary$cards$tbl_summary |> 
    mutate(
      variable = factor(variable, levels = names(label)),
      variable_label = factor(variable, levels = names(label),  labels = label),
    ) |>
    filter(!(context %in% c("missing", "attributes", "total_n"))) |>
    select(-fmt_fn, -warning, -error, -gts_column) |>
    pivot_wider(
      id_cols = c("group1", "group1_level", "variable", "variable_label", "variable_level", "context"), 
      names_from = stat_name, 
      values_from = stat
    ) |>
    mutate(
      across(
        c(n, N),
        ~{
          map_int(., ~{
            if(is.null(.)) NA else as.integer(.)
          })
        }
      ),
      across(
        c(p, median, p10, p25, p75, p90, mean, sd),
        ~{
          map_dbl(., ~{
            if(is.null(.)) NA else as.numeric(.)
          })
        }
      ),
      across(
        c(group1_level, variable_level),
        ~{
          map_chr(., ~{
            if(is.null(.)) NA else as.character(.)
          })
        }
      ),
    )|>
    arrange(variable_label, group1, group1_level)
  
  raw_stats_redacted <- 
    raw_stats |>
    mutate(
      n = roundmid_any(n, threshold),
      N = roundmid_any(N, threshold),
      p = n / N,
    )
  
  return(raw_stats_redacted)
}

roundmid_any <- function(x, to = 1) {
  # like ceiling_any, but centers on (integer) midpoint of the rounding points
  ceiling(x / to) * to - (floor(to / 2) * (x != 0))
}