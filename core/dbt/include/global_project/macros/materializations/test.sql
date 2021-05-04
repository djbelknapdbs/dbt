{%- materialization test, default -%}

  {% if flags.STORE_FAILURES %}

    {% set identifier = model['name'] %}
    {% set target_relation = api.Relation.create(
        identifier=identifier, schema=schema, database=database, type='table') -%} %}
    
    {% call statement(auto_begin=True) %}
        {{ create_table_as(False, target_relation, sql) }}
    {% endcall %}
  
    {% set main_sql %}
        select count(*) as validation_errors
        from {{ target_relation }}
    {% endset %}
    
    {{ adapter.commit() }}
  
  {% else %}

      {% set main_sql %}
          select count(*) as validation_errors
          from (
            {{ sql }}
          ) _dbt_internal_test
      {% endset %}
  
  {% endif %}

  {% call statement('main', fetch_result=True) -%}
    {{ main_sql }}
  {%- endcall %}

{%- endmaterialization -%}
