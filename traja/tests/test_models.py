import pandas as pd

import traja
from traja.dataset import dataset
from traja.dataset.example import jaguar
from traja.models import LSTM
from traja.models import MultiModelAE
from traja.models import MultiModelVAE
from traja.models.losses import Criterion
from traja.models.train import HybridTrainer


def test_aevae_jaguar():
    """
    Test Autoencoder and variational auto encoder models for training/testing/generative network and
    classification networks

    """

    # Sample data
    df = jaguar()

    # Hyperparameters
    batch_size = 10
    num_past = 10
    num_future = 5
    # Prepare the dataloader
    data_loaders = dataset.MultiModalDataLoader(df,
                                                batch_size=batch_size,
                                                n_past=num_past,
                                                n_future=num_future,
                                                train_split_ratio=0.5,
                                                num_workers=1,
                                                split_by_id=False)

    model_save_path = './model.pt'

    model = MultiModelVAE(input_size=2,
                          output_size=2,
                          lstm_hidden_size=32,
                          num_lstm_layers=2,
                          num_classes=9,
                          latent_size=10,
                          dropout=0.1,
                          num_classifier_layers=4,
                          classifier_hidden_size=32,
                          batch_size=batch_size,
                          num_future=num_future,
                          num_past=num_past,
                          bidirectional=False,
                          batch_first=True,
                          reset_state=True)

    # Test that we can run functions on our network.
    model.disable_latent_output()
    model.enable_latent_output()

    # Test that we can reset the classifier
    model.reset_classifier(classifier_hidden_size=32, num_classifier_layers=4)

    # Model Trainer
    # Model types; "ae" or "vae"
    trainer = HybridTrainer(model=model,
                            optimizer_type='Adam',
                            loss_type='huber')

    # Train the model
    trainer.fit(data_loaders, model_save_path, epochs=10, training_mode='forecasting')
    trainer.fit(data_loaders, model_save_path, epochs=10, training_mode='classification')

    scaler = data_loaders['train_loader'].dataset.scaler

    # Load the trained model given the path
    model_path = './model.pt'
    hyperparams = './hypers.json'
    model_hyperparameters = traja.models.read_hyperparameters(hyperparams)

    # For prebuild traja generative models
    generator = traja.models.inference.Generator(model_type='vae', model_hyperparameters=model_hyperparameters,
                                                 model_path=model_path, model=None)
    out = generator.generate(num_future, classify=False, scaler=scaler, plot_data=False)

    trainer.validate(data_loaders['validation_loader'])


def test_ae_jaguar():
    """
    Test Autoencoder and variational auto encoder models for training/testing/generative network and
    classification networks

    """

    # Sample data
    df = jaguar()

    # Hyperparameters
    batch_size = 10
    num_past = 10
    num_future = 5
    # Prepare the dataloader
    data_loaders = dataset.MultiModalDataLoader(df,
                                                batch_size=batch_size,
                                                n_past=num_past,
                                                n_future=num_future,
                                                num_workers=1,
                                                train_split_ratio=0.5,
                                                validation_split_ratio=0.2)

    model_save_path = './model.pt'

    model = MultiModelAE(input_size=2, num_past=num_past, batch_size=batch_size, num_future=num_future,
                         lstm_hidden_size=32, num_lstm_layers=2, output_size=2, latent_size=10, batch_first=True,
                         dropout=0.1, reset_state=True, bidirectional=False, num_classifier_layers=4,
                         classifier_hidden_size=32, num_classes=9)

    # Test that we can reset the classifier
    model.reset_classifier(classifier_hidden_size=32, num_classifier_layers=4)


    # Model Trainer
    # Model types; "ae" or "vae"
    trainer = HybridTrainer(model=model,
                            optimizer_type='Adam',
                            loss_type='huber')

    # Train the model
    trainer.fit(data_loaders, model_save_path, epochs=10, training_mode='forecasting')
    trainer.fit(data_loaders, model_save_path, epochs=10, training_mode='classification')

    trainer.validate(data_loaders['sequential_validation_loader'])


def test_lstm_jaguar():
    """
    Testing method for lstm model used for forecasting.
    """

    # Sample data
    df = jaguar()

    # Hyperparameters
    batch_size = 10
    num_past = 10
    num_future = 10

    # For timeseries prediction
    assert num_past == num_future

    # Prepare the dataloader
    data_loaders = dataset.MultiModalDataLoader(df,
                                                batch_size=batch_size,
                                                n_past=num_past,
                                                n_future=num_future,
                                                num_workers=1)

    model_save_path = './model.pt'

    # Model init
    model = LSTM(input_size=2,
                 hidden_size=32,
                 num_layers=2,
                 output_size=2,
                 dropout=0.1,
                 batch_size=batch_size,
                 num_future=num_future,
                 bidirectional=False,
                 batch_first=True,
                 reset_state=True)

    # Model Trainer
    trainer = HybridTrainer(model=model,
                            optimizer_type='Adam',
                            loss_type='huber')
    # Train the model
    trainer.fit(data_loaders, model_save_path, epochs=2, training_mode='forecasting')


def test_aevae_regression_network_converges():
    """
    Test Autoencoder and variational auto encoder models for training/testing/generative network and
    classification networks

    """

    data = list()
    num_ids = 3

    for sample_id in range(num_ids):
        for sequence in range(70 + sample_id * 4):
            parameter_one = 0.2 * sample_id
            parameter_two = 91.235 * sample_id
            data.append([sequence, sequence, sample_id, parameter_one, parameter_two])
    # Sample data
    df = pd.DataFrame(data, columns=['x', 'y', 'ID', 'parameter_one', 'parameter_two'])

    parameter_columns = ['parameter_one', 'parameter_two']

    # Hyperparameters
    batch_size = 1
    num_past = 10
    num_future = 5
    # Prepare the dataloader
    data_loaders = dataset.MultiModalDataLoader(df,
                                                batch_size=batch_size,
                                                n_past=num_past,
                                                n_future=num_future,
                                                train_split_ratio=0.333,
                                                validation_split_ratio=0.333,
                                                num_workers=1,
                                                parameter_columns=parameter_columns,
                                                split_by_id=False,
                                                stride=1)

    model_save_path = './model.pt'

    model = MultiModelVAE(input_size=2,
                          output_size=2,
                          lstm_hidden_size=32,
                          num_lstm_layers=2,
                          num_regressor_parameters=len(parameter_columns),
                          latent_size=10,
                          dropout=0.1,
                          num_regressor_layers=4,
                          regressor_hidden_size=32,
                          batch_size=batch_size,
                          num_future=num_future,
                          num_past=num_past,
                          bidirectional=False,
                          batch_first=True,
                          reset_state=True)

    # Test resetting the regressor, to make sure this function works
    model.reset_regressor(regressor_hidden_size=32, num_regressor_layers=4)

    # Model Trainer
    # Model types; "ae" or "vae"
    trainer = HybridTrainer(model=model,
                            optimizer_type='Adam',
                            loss_type='mse')

    criterion = Criterion()
    loss_pre_training = 0.
    for data, _, _, parameters in data_loaders['train_loader']:
        prediction = model(data.float(), regress=True, latent=False)
        loss_pre_training += criterion.regressor_criterion(prediction, parameters)

    print(f'Loss pre training: {loss_pre_training}')

    # Train the model
    trainer.fit(data_loaders, model_save_path, epochs=2, training_mode='forecasting')
    trainer.fit(data_loaders, model_save_path, epochs=2, training_mode='regression')

    loss_post_training = 0.
    for data, _, _, parameters in data_loaders['train_loader']:
        prediction = model(data.float(), regress=True, latent=False)
        loss_post_training += criterion.regressor_criterion(prediction, parameters)

    print(f'Loss post training: {loss_post_training}')
    assert loss_post_training < loss_pre_training


def test_ae_regression_network_converges():
    """
    Test Autoencoder and variational auto encoder models for training/testing/generative network and
    classification networks

    """

    data = list()
    num_ids = 3

    for sample_id in range(num_ids):
        for sequence in range(70 + sample_id * 4):
            parameter_one = 0.2 * sample_id
            parameter_two = 91.235 * sample_id
            data.append([sequence, sequence, sample_id, parameter_one, parameter_two])
    # Sample data
    df = pd.DataFrame(data, columns=['x', 'y', 'ID', 'parameter_one', 'parameter_two'])

    parameter_columns = ['parameter_one', 'parameter_two']

    # Hyperparameters
    batch_size = 1
    num_past = 10
    num_future = 5
    # Prepare the dataloader
    data_loaders = dataset.MultiModalDataLoader(df,
                                                batch_size=batch_size,
                                                n_past=num_past,
                                                n_future=num_future,
                                                train_split_ratio=0.333,
                                                validation_split_ratio=0.333,
                                                num_workers=1,
                                                parameter_columns=parameter_columns,
                                                split_by_id=False,
                                                stride=1)

    model_save_path = './model.pt'

    model = MultiModelAE(input_size=2,
                         output_size=2,
                          lstm_hidden_size=32,
                          num_lstm_layers=2,
                          num_regressor_parameters=len(parameter_columns),
                          latent_size=10,
                          dropout=0.1,
                          num_regressor_layers=4,
                          regressor_hidden_size=32,
                          batch_size=batch_size,
                          num_future=num_future,
                          num_past=num_past,
                          bidirectional=False,
                          batch_first=True,
                          reset_state=True)

    # Test resetting the regressor, to make sure this function works
    model.reset_regressor(regressor_hidden_size=32, num_regressor_layers=4)

    # Model Trainer
    # Model types; "ae" or "vae"
    trainer = HybridTrainer(model=model,
                            optimizer_type='Adam',
                            loss_type='mse')

    criterion = Criterion()
    loss_pre_training = 0.
    for data, _, _, parameters in data_loaders['train_loader']:
        prediction = model(data.float(), regress=True, latent=False)
        loss_pre_training += criterion.regressor_criterion(prediction, parameters)

    print(f'Loss pre training: {loss_pre_training}')

    # Train the model
    trainer.fit(data_loaders, model_save_path, epochs=2, training_mode='forecasting')
    trainer.fit(data_loaders, model_save_path, epochs=2, training_mode='regression')

    loss_post_training = 0.
    for data, _, _, parameters in data_loaders['train_loader']:
        prediction = model(data.float(), regress=True, latent=False)
        loss_post_training += criterion.regressor_criterion(prediction, parameters)

    print(f'Loss post training: {loss_post_training}')
    assert loss_post_training < loss_pre_training