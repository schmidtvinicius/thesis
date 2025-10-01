from pyflink.common import Row, WatermarkStrategy
from pyflink.common.serialization import Encoder
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.file_system import (FileSink,
                                                       OutputFileConfig)
from pyflink.datastream.connectors.jdbc import (JdbcConnectionOptions,
                                                JdbcExecutionOptions, JdbcSink)
from pyflink.datastream.connectors.number_seq import NumberSequenceSource
from pyflink.datastream.functions import MapFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor


class MyMapFunction(MapFunction):

    def open(self, runtime_context: RuntimeContext):
        state_desc = ValueStateDescriptor('cnt', Types.PICKLED_BYTE_ARRAY())
        self.cnt_state = runtime_context.get_state(state_desc)


    def map(self, value):
        return value[0], value[1], value[2]


def state_access_demo():
    # 1. create a StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # 2. create source DataStream
    seq_num_source = NumberSequenceSource(1, 10000)
    ds = env.from_source(
        source=seq_num_source,
        watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
        source_name='seq_num_source',
        type_info=Types.LONG())

    # 3. define the execution logic
    ds = ds.map(lambda a: Row(a, a*2, a**2), output_type=Types.ROW([Types.LONG(), Types.LONG(), Types.LONG()])) \
           .key_by(lambda a: a[0]) \
           .map(MyMapFunction(), output_type=Types.TUPLE([Types.LONG(), Types.LONG(), Types.LONG()]))

    # 4. create sink and emit result to sink
    # output_path = '.'
    # file_sink = FileSink \
    #     .for_row_format(output_path, Encoder.simple_string_encoder()) \
    #     .with_output_file_config(OutputFileConfig.builder().with_part_prefix('pre').with_part_suffix('suf').build()) \
    #     .build()
    # ds.sink_to(file_sink)
    sink = JdbcSink.sink(
        "INSERT INTO numbers (original, double, square)",
        Types.ROW([Types.LONG(), Types.LONG(), Types.LONG()]),
        JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
            .with_url('jdbc:duckdb:ducklake:aws-1-us-east-2.pooler.supabase.com')
            .with_driver_name('org.duckdb.DuckDBDriver')
            .with_user_name('postgres.rvifiqhlbglcxdfhpxso')
            .with_password('ZbuN0TnDNot5IqIC')
        )
    # ds.add_sink(sink)
    ds.print()

    # 5. execute the job
    env.execute('state_access_demo')


if __name__ == '__main__':
    state_access_demo()
