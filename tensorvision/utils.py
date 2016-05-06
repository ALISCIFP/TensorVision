from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from datetime import datetime
import time
import os
import logging


# Add basic configuration
def cfg():
    """General configuration values."""
    return None


def _set_cfg_value(cfg_name, env_name, default, cfg):
    """
    Set a value for the configuration.

    Parameters
    ----------
    cfg_name : str
    env_name : str
    default : str
    cfg : function
    """
    if env_name in os.environ:
        setattr(cfg, cfg_name, os.environ[env_name])
    else:
        logging.info("No environment variable '%s' found. Set to '%s'.",
                     env_name,
                     default)
        setattr(cfg, cfg_name, default)

_set_cfg_value('data_dir', 'TV_DATA_DIR', 'DATA', cfg)
_set_cfg_value('model_dir', 'TV_MODEL_DIR', 'output', cfg)
_set_cfg_value('default_config',
               'TV_DEFAULT_CONFIG_PATH',
               'examples/cifar10_minimal.json',
               cfg)
_set_cfg_value('plugin_dir',
               'TV_PLUGIN_DIR',
               os.path.expanduser("~/tv-plugins"),
               cfg)
_set_cfg_value('step_show', 'TV_STEP_SHOW', 100, cfg)
_set_cfg_value('step_str',
               'TV_STEP_STR',
               ('Step {step}/{total_steps}: loss = {loss_value:.2f} '
                '( {sec_per_batch:.3f} sec (per Batch); '
                '{examples_per_sec:.1f} examples/sec)'),
               cfg)


def load_plugins():
    """Load all TV plugins."""
    if os.path.isdir(cfg.plugin_dir):
        onlyfiles = [f for f in os.listdir(cfg.plugin_dir)
                     if os.path.isfile(os.path.join(cfg.plugin_dir, f))]
        pyfiles = [f for f in onlyfiles if f.endswith('.py')]
        import imp
        for pyfile in pyfiles:
            logging.info('Loaded plugin "%s".', pyfile)
            imp.load_source(os.path.splitext(os.path.basename(pyfile))[0],
                            pyfile)


# Basic model parameters as external flags.
flags = tf.app.flags
FLAGS = flags.FLAGS

tf.app.flags.DEFINE_boolean('debug', False, 'Soggy Leaves')


# usage: train.py --config=my_model_params.py
flags.DEFINE_string('hypes', cfg.default_config,
                    'File storing model parameters.')
load_plugins()


def get_train_dir(hypes_fname):
    if FLAGS.debug:
        train_dir = os.path.join(cfg.model_dir, 'debug')
        logging.info(
            "Saving/Loading Model from debug Folder: %s ", train_dir)
        logging.info("Use --name=MYNAME to use Folder: %s ",
                     os.path.join(cfg.model_dir, "MYNAME"))
    else:
        json_name = hypes_fname.split('/')[-1].replace('.json', '')
        date = datetime.now().strftime('%Y_%m_%d_%H.%M')
        run_name = '%s_%s' % (json_name, date)
        train_dir = os.path.join(cfg.model_dir, run_name)\

    return train_dir


# TODO: right place to store placeholders

def placeholder_inputs(batch_size):
    """Generate placeholder variables to represent the the input tensors.

    These placeholders are used as inputs by the rest of the model building
    code and will be fed from the downloaded data in the .run() loop, below.

    Args:
      batch_size: The batch size will be baked into both placeholders.

    Returns:
      images_placeholder: Images placeholder.
      labels_placeholder: Labels placeholder.
      keep_prob: keep_prob placeholder.
    """
    # Note that the shapes of the placeholders match the shapes of the full
    # image and label tensors, except the first dimension is now batch_size
    # rather than the full size of the train or test data sets.

    keep_prob = tf.placeholder("float")
    return keep_prob


def fill_feed_dict(kb, train):
    """Fills the feed_dict for training the given step.

    A feed_dict takes the form of:
    feed_dict = {
        <placeholder>: <tensor of values to be passed for placeholder>,
        ....
    }

    Args:
      kb: The keep prob placeholder.
      train: whether data set is on train.

    Returns:
      feed_dict: The feed dictionary mapping from placeholders to values.
    """
    # Create the feed_dict for the placeholders filled with the next
    # `batch size ` examples.

    if train:
        feed_dict = {
            kb: 0.5}
    else:
        feed_dict = {
            kb: 1.0}
    return feed_dict


# TODO: right place to store eval?
