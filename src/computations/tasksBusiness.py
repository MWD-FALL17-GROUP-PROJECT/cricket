# -*- coding: utf-8 -*-

from computations import decompositions
from data import DataHandler
import pandas as pd
from collections import defaultdict
from operator import itemgetter
from util import constants
from util import formatter
import numpy as np
from computations import metrics
from computations import personalizedpagerank as ppr
DataHandler.vectors()

def genre_spaceTags_LDA(genre):
    DataHandler.vectors()
    movie_tag_map,tag_id_map,actor_movie_rank_map,movie_actor_rank_map = DataHandler.get_dicts()
    df = DataHandler.load_genre_matrix(genre)
    ldaModel,doc_term_matrix,id_Term_map  =  decompositions.LDADecomposition(df,5,constants.genreTagsSpacePasses)
    topic_terms = defaultdict(set)
    for i in range(0,5):
        for tuples in ldaModel.get_topic_terms(i):#get_topics_terms returns top n(default = 10) words of the topics
            term = tag_id_map.get(id_Term_map.get(tuples[0]))
            topic_terms[i].add((term,tuples[1]))
    for i in range(0,5):
        print(sorted(topic_terms.get(i),key = itemgetter(1),reverse=True))
        print('\n')
    return

def genre_spaceActors_LDA(genre):
    movie_tag_map,tag_id_map,actor_movie_rank_map,movie_actor_rank_map = DataHandler.get_dicts()
    df = DataHandler.load_genre_actor_matrix(genre)
    ldaModel,doc_term_matrix,id_Term_map  =  decompositions.LDADecomposition(df,5,constants.genreActorSpacePasses)
    topic_terms = defaultdict(set)
    for i in range(0,5):
        for tuples in ldaModel.get_topic_terms(i):#get_topics_terms returns top n(default = 10) words of the topics
            term = id_Term_map.get(tuples[0])
            topic_terms[i].add((term,tuples[1]))
    for i in range(0,5):
        print(sorted(topic_terms.get(i),key = itemgetter(1),reverse=True))
        print('\n')

        
def top10_Actors_LDA(givenActor):
    DataHandler.create_actor_actorid_map()
    top10SimilarActors_similarity = DataHandler.similarActors_LDA(givenActor)
    print('Actors similar to '+str(DataHandler.actor_actorid_map[givenActor]))
    for actor,sim in top10SimilarActors_similarity:
        print(DataHandler.actor_actorid_map[actor]+' '+str(sim))

def prettyPrintVector(vector, actorsInDf, actorIdActorsDf, indexId):
    vectorLen = len(vector)
    for index in range(0, vectorLen):
        actorId = actorsInDf[index]
        actorName = actorIdActorsDf[actorIdActorsDf[indexId]==actorId].iloc[0][1]
        print(actorName + ": " + str(vector[index]), end=', ')
    print('.')
    
def prettyPrintYearVector(vector, actorsInDf, actorIdActorsDf, indexId):
    vectorLen = len(vector)
    for index in range(0, vectorLen):
        actorId = actorsInDf[index]
        actorName = actorIdActorsDf[actorIdActorsDf[indexId]==actorId].iloc[0][2]
        print(str(actorName) + ": " + str(vector[index]), end=', ')
    print('.')
    
def prettyPrintRankVector(vector, actorsInDf, actorIdActorsDf, indexId):
    vectorLen = len(vector)
    for index in range(0, vectorLen):
        actorId = actorsInDf[index]
        actorName = actorIdActorsDf[actorIdActorsDf[indexId]==actorId].iloc[0][3]
        print(str(actorName) + ": " + str(vector[index]), end=', ')
    print('.')
    
def top5LatentCP(tensorIdentifier, space):
    if (tensorIdentifier == 'AMY'):
        tensor, actors, movies, years = DataHandler.getTensor_ActorMovieYear()
        u = decompositions.CPDecomposition(tensor, constants.RANK)
        if (space == 'Actor'):
            actorIdActorsDf = DataHandler.actor_info_df
            actorRank = np.array(u[0])
            split_group_with_index = formatter.splitGroup(actorRank, 5)
            get_partition_on_ids(split_group_with_index, actorIdActorsDf['name'])
            semantics = np.matrix(actorRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintVector(semantic, actors, actorIdActorsDf, 'id')
                print("")
            
            return
        if (space == 'Movie'):
            movieIdMoviesDf = DataHandler.genre_movie_df
            movieRank = np.array(u[1])
            split_group_with_index = formatter.splitGroup(movieRank, 5)
            get_partition_on_ids(split_group_with_index, movieIdMoviesDf['moviename'])
            
            semantics = np.matrix(movieRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintVector(semantic, movies, movieIdMoviesDf, 'movieid')
                print("")
                
            return
        if (space == 'Year'):
            movieIdMoviesDf = DataHandler.genre_movie_df
            YearRank = np.array(u[2])
            split_group_with_index = formatter.splitGroup(YearRank, 5)
            get_partition_on_ids(split_group_with_index, years)
            
            semantics = np.matrix(YearRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintYearVector(semantic, years, movieIdMoviesDf, 'year')
                print("")
                
            return
        else:
            print('Wrong Space')
            return
    if (tensorIdentifier == 'TMR'):
        tensor, tags, movies, ranks = DataHandler.getTensor_TagMovieRating()
        u = decompositions.CPDecomposition(tensor,constants.RANK)
        if (space == 'Tag'):
            tagIdTagsDf = DataHandler.tag_id_df
            tagRank = np.array(u[0])
            split_group_with_index = formatter.splitGroup(tagRank, 5)
            get_partition_on_ids(split_group_with_index, tagIdTagsDf['tag'])
            semantics = np.matrix(tagRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintVector(semantic, tags, tagIdTagsDf, 'tagId')
                print("")
                
            return
        if (space == 'Movie'):
            movieIdMoviesDf = DataHandler.genre_movie_df
            movieRank = np.array(u[1])
            split_group_with_index = formatter.splitGroup(movieRank, 5)
            get_partition_on_ids(split_group_with_index, movieIdMoviesDf['moviename'])
            semantics = np.matrix(movieRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintVector(semantic, movies, movieIdMoviesDf, 'movieid')
                print("")
                
            return
        if (space == 'Rating'):
            userRatings = DataHandler.user_ratings_df
            RankingRank = np.array(u[2])
            split_group_with_index = formatter.splitGroup(RankingRank, 5)
            get_partition_on_ids(split_group_with_index, ranks)
            semantics = np.matrix(RankingRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintRankVector(semantic, ranks, userRatings, 'rating')
                print("")
                
            return
        else:
            print('Wrong Space')
            return
    else:
        print('Wrong Tensor Identifier')

data_required = {}

def get_partition_on_ids(split_group_with_index, data) :
    data_required.clear()
    for i in range(len(split_group_with_index)):
      for j in range(len(split_group_with_index[i])):
         if i in data_required :
             data_required.get(i).append(data[split_group_with_index[i][j]])
         else :
             data_required.update({i : [data[split_group_with_index[i][j]]]})
    
    return data_required
    
def get_partition_subtasks() :
    for x, v in data_required.items() :
        print ('Group ' + str(x+1) + ' : ' + str(v))
        print (" ")
    #print(data_required)
        
#def PPR_top10_SimilarActors(seed):
#    DataHandler.createDictionaries1()
#    DataHandler.create_actor_actorid_map()
#    actact = DataHandler.actor_actor_similarity_matrix()
#    actor_actorid_map = DataHandler.actor_actorid_map
#    alpha = constants.ALPHA
#    act_similarities = pagerank.PPR(actact,seed,alpha)
#    print('Top 10 actors similar to the following seed actors: '+str([actor_actorid_map.get(i) for i in seed]))
#    for index,sim in act_similarities:
#        print(actor_actorid_map.get(actact.columns[index])+' '+ str(sim))
#        
#def PPR_top10_SimilarCoActors(seed):
#    DataHandler.createDictionaries1()
#    DataHandler.create_actor_actorid_map()
#    actact = DataHandler.actor_actor_similarity_matrix()
#    actor_actorid_map = DataHandler.actor_actorid_map
#    alpha = constants.ALPHA
#    act_similarities = pagerank.PPR(actact,seed,alpha)
#    print('Co Actors similar to the following seed actors: '+str([actor_actorid_map.get(i) for i in seed]))
#    for index,sim in act_similarities:
#        print(actor_actorid_map.get(actact.columns[index])+' '+ str(sim))
#
##userMovies = user_rated_or_tagged_map.get(67348)
#def top5SimilarMovies(userMovies):
#    DataHandler.createDictionaries1()
#    u = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenreYear(),5)
#    movies = sorted(list(DataHandler.movie_actor_map.keys()))
#    u1= u[1]
#    movieNewDSpace = pd.DataFrame(u1,index = movies)
#    movie_movie_similarity = DataHandler.movie_movie_Similarity(movieNewDSpace)
#    movieid_name_map = DataHandler.movieid_name_map
#    alpha = constants.ALPHA
#    movie_similarities = pagerank.PPR(movie_movie_similarity,userMovies,alpha)
#    print('Movies similar to the following seed movies: '+str([movieid_name_map.get(i) for i in userMovies]))
#    for index,sim in movie_similarities:
#        if (movie_movie_similarity.columns[index] not in userMovies):
#            print(movieid_name_map.get(movie_movie_similarity.columns[index])+' '+ str(sim))

	
def PersnalizedPageRank_top10_SimilarActors(seed):
    DataHandler.createDictionaries1()
    DataHandler.create_actor_actorid_map()
    actact = DataHandler.actor_actor_invSimilarity_matrix()
    actor_actorid_map = DataHandler.actor_actorid_map
    alpha = constants.ALPHA
    act_similarities = ppr.personalizedPageRank(actact,seed,alpha)
    actors = list(actact.index)
    actorDF = pd.DataFrame(pd.Series(actors),columns = ['Actor'])
    actorDF['Actor'] = actorDF['Actor'].map(lambda x:actor_actorid_map.get(x))
    Result = pd.concat([act_similarities,actorDF],axis = 1)
    sortedResult=Result.sort_values(by=0,ascending=False).head(15)
    seedAcotorNames = [actor_actorid_map.get(i) for i in seed]
    print('Actors similar to the following seed actors: '+str(seedAcotorNames))
    for index in sortedResult.index:
        if sortedResult.loc[index,'Actor'] not in seedAcotorNames:
            print(sortedResult.loc[index,'Actor']+' '+ str(sortedResult.loc[index,0]))
        
def PersnalizedPageRank_top10_SimilarCoActors(seed):
    DataHandler.createDictionaries1()
    DataHandler.create_actor_actorid_map()
    coactcoact, ignoreVariable = DataHandler.coactor_siilarity_matrix()
    actor_actorid_map = DataHandler.actor_actorid_map
    alpha = constants.ALPHA
    act_similarities = ppr.personalizedPageRank(coactcoact,seed,alpha)
    actors = list(coactcoact.index)
    actorDF = pd.DataFrame(pd.Series(actors),columns = ['Actor'])
    actorDF['Actor'] = actorDF['Actor'].map(lambda x:actor_actorid_map.get(x))
    Result = pd.concat([act_similarities,actorDF],axis = 1)
    sortedResult=Result.sort_values(by=0,ascending=False).head(15)
    seedAcotorNames = [actor_actorid_map.get(i) for i in seed]
    print('Co Actors similar to the following seed actors: '+str(seedAcotorNames))
    for index in sortedResult.index:
        if sortedResult.loc[index,'Actor'] not in seedAcotorNames:
            print(sortedResult.loc[index,'Actor']+' '+ str(sortedResult.loc[index,0]))

#userMovies = user_rated_or_tagged_map.get(67348)
#userMovies = user_rated_or_tagged_map.get(3)
def PersnalizedPageRank_top5SimilarMovies(userMovies):
    DataHandler.createDictionaries1()
    u = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenreYearRankRating(),5)
    movies = sorted(list(DataHandler.movie_actor_map.keys()))
    u1= u[1]
    movieNewDSpace = pd.DataFrame(u1,index = movies)
    movie_movie_similarity = DataHandler.movie_movie_Similarity(movieNewDSpace)
    movieid_name_map = DataHandler.movieid_name_map
    alpha = constants.ALPHA
    movie_similarities = ppr.personalizedPageRank(movie_movie_similarity,userMovies,alpha)
    movies = list(movie_movie_similarity.index)
    movieDF = pd.DataFrame(pd.Series(movies),columns = ['movies'])
    movieDF['movies'] = movieDF['movies'].map(lambda x:movieid_name_map.get(x))
    Result = pd.concat([movie_similarities,movieDF],axis = 1)
    sortedResult=Result.sort_values(by=0,ascending=False).head(15)
    seedmovieNames = [movieid_name_map.get(i) for i in userMovies]
    print('Movies similar to the following seed movies: '+str(seedmovieNames))
    movie_genre_map = DataHandler.movie_genre_map
    genreForSeedMovies = [movie_genre_map.get(i) for i in userMovies]    
    print('Genres for seed movies: '+str(genreForSeedMovies))
    for index in sortedResult.index:
        if sortedResult.loc[index,'movies'] not in seedmovieNames:
            print(sortedResult.loc[index,'movies']+' '+ str(sortedResult.loc[index,0])+' '+str(movie_genre_map.get(movies[index])))


def top5SimilarMovies1(userMovies):
    DataHandler.createDictionaries1()
    u = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenreYearRankRating(),5)
    movies = sorted(list(DataHandler.movie_actor_map.keys()))
    u1= u[1]
    movieNewDSpace = pd.DataFrame(u1,index = movies)
    movie_movie_similarity = DataHandler.movie_movie_Similarity1(movieNewDSpace)
    movieid_name_map = DataHandler.movieid_name_map
    alpha = constants.ALPHA
    movie_similarities = pagerank.PPR(movie_movie_similarity,userMovies,alpha)
    print('Movies similar to the following seed movies: '+str([movieid_name_map.get(i) for i in userMovies]))
    for index,sim in movie_similarities:
        if (movie_movie_similarity.columns[index] not in userMovies):
            print(movieid_name_map.get(movie_movie_similarity.columns[index])+' '+ str(sim))

            
def PersnalizedPageRank_top5SimilarMovies1(userMovies):
    DataHandler.createDictionaries1()
    u = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenreYearRankRating(),5)
    movies = sorted(list(DataHandler.movie_actor_map.keys()))
    u1= u[1]
    movieNewDSpace = pd.DataFrame(u1,index = movies)
    movie_movie_similarity = DataHandler.movie_movie_Similarity1(movieNewDSpace)
    movieid_name_map = DataHandler.movieid_name_map
    alpha = constants.ALPHA
    movie_similarities = ppr.personalizedPageRank(movie_movie_similarity,userMovies,alpha)
    movies = list(movie_movie_similarity.index)
    movieDF = pd.DataFrame(pd.Series(movies),columns = ['movies'])
    movieDF['movies'] = movieDF['movies'].map(lambda x:movieid_name_map.get(x))
    Result = pd.concat([movie_similarities,movieDF],axis = 1)
    sortedResult=Result.sort_values(by=0,ascending=False).head(15)
    seedmovieNames = [movieid_name_map.get(i) for i in userMovies]
    print('Movies similar to the following seed movies: '+str(seedmovieNames))
    movie_genre_map = DataHandler.movie_genre_map
    genreForSeedMovies = [movie_genre_map.get(i) for i in userMovies]    
    print('Genres for seed movies: '+str(genreForSeedMovies))
    for index in sortedResult.index:
        if sortedResult.loc[index,'movies'] not in seedmovieNames:
            print(sortedResult.loc[index,'movies']+' '+ str(sortedResult.loc[index,0])+' '+str(movie_genre_map.get(movies[index])))

def Recommender(userId):
    DataHandler.createDictionaries1()
    movieRatedSeed = DataHandler.userMovieRatings(userId)
    
    
    actor_movie_rank_map = DataHandler.actor_movie_rank_map
    decomposed = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenre(),5)
    moviesList = sorted(list(DataHandler.movie_actor_rank_map.keys()))
    movie_movie_similarity = DataHandler.movie_movie_Similarity1(pd.DataFrame(decomposed[1],index=moviesList))
    prData = ppr.personalizedPageRankWeighted(movie_movie_similarity, movieRatedSeed, 0.9)
    rankedItems = sorted(list(map(lambda x:(moviesList[x[0]],x[1]),prData.itertuples())),key=lambda x:x[1], reverse=True)
    movieid_name_map = DataHandler.movieid_name_map

    seedmovieNames = [movieid_name_map[k] for k,y in movieRatedSeed]
    print("Movies similar to the users seed movies " + str(seedmovieNames) + " are:")
    return [(movieid_name_map[k],y) for (k,y) in rankedItems if k not in [k for k,y in movieRatedSeed]]











