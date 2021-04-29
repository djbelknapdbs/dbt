from dbt.context.context_config import ContextConfig
from dbt.contracts.graph.parsed import ParsedModelNode
from dbt.dbt_jinja.compiler import extract_from_source
from dbt.node_types import NodeType
from dbt.parser.base import IntermediateNode, SimpleSQLParser
from dbt.parser.search import FileBlock


class ModelParser(SimpleSQLParser[ParsedModelNode]):
    def parse_from_dict(self, dct, validate=True) -> ParsedModelNode:
        if validate:
            ParsedModelNode.validate(dct)
        return ParsedModelNode.from_dict(dct)

    @property
    def resource_type(self) -> NodeType:
        return NodeType.Model

    @classmethod
    def get_compiled_path(cls, block: FileBlock):
        return block.path.relative_path

    def render_update(
        self, node: IntermediateNode, config: ContextConfig
    ) -> None:
        # run dbt-jinja extractor (powered by tree-sitter)
        res = extract_from_source(node.raw_sql)

        # if it doesn't need python jinja, fit the refs, sources, and configs
        # into the node. Down the line the rest of the node will be updated with
        # this information. (e.g. depends_on etc.)
        if not res['python_jinja']:
            node.refs = node.refs + res['refs']
            for sourcev in res['sources']:
                # TODO change extractor to match type here
                node.sources.append([sourcev[0], sourcev[1]])
            for configv in res['configs']:
                node.config[configv[0]] = configv[1]

            # if the extracted configs have any of the special ones,
            # this will merge them into node.config
            self.update_parsed_node_config(node, dict(res['configs']))

            # TODO this is probably wrong
            node.unrendered_config = dict(res['configs'])
        else:
            super().render_update(node, config)
