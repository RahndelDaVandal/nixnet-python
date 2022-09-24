from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import sys
import time

import six

import nixnet
from nixnet import constants


def convert_timestamp(timestamp):
    system_epoch = time.gmtime(0)
    system_epock_datetime = datetime.datetime(system_epoch.tm_year, system_epoch.tm_mon, system_epoch.tm_mday)
    xnet_epoch_datetime = datetime.datetime(1601, 1, 1)
    delta = system_epock_datetime - xnet_epoch_datetime
    return datetime.datetime.fromtimestamp(timestamp * 100e-9) - delta


def main():
    database_name = 'NIXNET_example'
    cluster_name = 'CAN_Cluster'
    input_signals = ['CANEventSignal1', 'CANEventSignal2']
    output_signals = ['CANEventSignal1', 'CANEventSignal2']
    interface1 = 'CAN1'
    interface2 = 'CAN2'

    with nixnet.SignalInSinglePointSession(
                interface1,
                database_name,
                cluster_name,
                input_signals) as input_session:
        with nixnet.SignalOutSinglePointSession(
                        interface2,
                        database_name,
                        cluster_name,
                        output_signals) as output_session:
            terminated_cable = six.moves.input('Are you using a terminated cable (Y or N)? ')
            if terminated_cable.lower() == "y":
                input_session.intf.can_term = constants.CanTerm.ON
                output_session.intf.can_term = constants.CanTerm.OFF
            elif terminated_cable.lower() == "n":
                input_session.intf.can_term = constants.CanTerm.ON
                output_session.intf.can_term = constants.CanTerm.ON
            else:
                print(f"Unrecognised input ({terminated_cable}), assuming 'n'")
                input_session.intf.can_term = constants.CanTerm.ON
                output_session.intf.can_term = constants.CanTerm.ON

            # Start the input session manually to make sure that the first
            # signal value sent before the initial read will be received.
            input_session.start()

            user_value = six.moves.input(
                f'Enter {len(input_signals)} signal values [float, float]: '
            )

            try:
                value_buffer = [float(x.strip()) for x in user_value.split(",")]
            except ValueError:
                value_buffer = [24.5343, 77.0129]
                print(
                    f'Unrecognized input ({user_value}). Setting data buffer to {value_buffer}'
                )


            if len(value_buffer) != len(input_signals):
                value_buffer = [24.5343, 77.0129]
                print(
                    f'Invalid number of signal values entered. Setting data buffer to {value_buffer}'
                )


            print('The same values should be received. Press q to quit')
            i = 0
            while True:
                for index, value in enumerate(value_buffer):
                    value_buffer[index] = value + i
                output_session.signals.write(value_buffer)
                print(f'Sent signal values: {value_buffer}')

                # Wait 1 s and then read the received values.
                # They should be the same as the ones sent.
                time.sleep(1)

                signals = input_session.signals.read()
                for timestamp, value in signals:
                    date = convert_timestamp(timestamp)
                    print(f'Received signal with timestamp {date} and value {value}')

                i += 1
                if max(value_buffer) + i > sys.float_info.max:
                    i = 0

                inp = six.moves.input('Hit enter to continue (q to quit): ')
                if inp.lower() == 'q':
                    break

            print('Data acquisition stopped.')


if __name__ == '__main__':
    main()
